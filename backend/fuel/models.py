from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
import uuid


class FuelSite(models.Model):
    """Fuel sites (gas stations, on-site tanks, charging stations)"""
    SITE_TYPE_CHOICES = [
        ('onsite', 'On-site Tank'),
        ('retail', 'Retail Station'),
        ('charging', 'EV Charging Station'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    site_type = models.CharField(max_length=20, choices=SITE_TYPE_CHOICES, default='retail')
    address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    time_zone = models.CharField(max_length=50, default='UTC')
    
    # Products supported (stored as JSON array)
    products_supported = models.JSONField(default=list, help_text="List of fuel products available")
    
    # Integration fields
    controller_type = models.CharField(max_length=100, blank=True, null=True, 
                                     help_text="FuelMaster, Veeder-Root, etc.")
    external_id = models.CharField(max_length=100, blank=True, null=True,
                                 help_text="External system identifier")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['site_type']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_site_type_display()})"


class FuelTransaction(models.Model):
    """Individual fuel transactions/fills"""
    ENTRY_SOURCE_CHOICES = [
        ('manual', 'Manual Entry'),
        ('csv_import', 'CSV Import'),
        ('fuel_card', 'Fuel Card Integration'),
        ('tank_controller', 'Tank Controller'),
        ('ev_charger_api', 'EV Charger API'),
    ]
    
    PRODUCT_TYPE_CHOICES = [
        ('gasoline', 'Gasoline'),
        ('diesel', 'Diesel'),
        ('def', 'Diesel Exhaust Fluid (DEF)'),
        ('cng', 'Compressed Natural Gas'),
        ('lng', 'Liquefied Natural Gas'),
        ('propane', 'Propane'),
        ('electricity', 'Electricity'),
        ('other', 'Other'),
    ]
    
    UNIT_CHOICES = [
        ('gal', 'Gallons'),
        ('L', 'Liters'),
        ('kWh', 'Kilowatt Hours'),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='fuel_transactions')
    timestamp = models.DateTimeField(default=timezone.now)
    entry_source = models.CharField(max_length=20, choices=ENTRY_SOURCE_CHOICES, default='manual')
    
    # Fuel details
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    volume = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(Decimal('0.001'))])
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='gal')
    unit_price = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True,
                                   help_text="Price per unit (cents for currency)")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                   help_text="Total cost in currency minor units (cents)")
    
    # Vehicle state at time of fill
    odometer = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True,
                                 help_text="Odometer reading in miles/km")
    engine_hours = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True,
                                     help_text="Engine hours at time of fill")
    
    # Location data
    location_latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    location_longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    location_label = models.CharField(max_length=255, blank=True, null=True,
                                    help_text="Site name or address")
    
    # Transaction metadata
    payment_ref = models.CharField(max_length=100, blank=True, null=True,
                                 help_text="Card transaction ID or receipt number")
    vendor = models.CharField(max_length=200, blank=True, null=True,
                            help_text="Station name or vendor")
    fuel_site = models.ForeignKey(FuelSite, on_delete=models.SET_NULL, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Audit trail
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='fuel_transactions_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Computed fields (calculated on save)
    distance_delta = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True,
                                       help_text="Distance since last fuel transaction")
    mpg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True,
                            help_text="Miles per gallon for this fill")
    cost_per_mile = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True,
                                      help_text="Cost per mile for this transaction")
    fuel_per_hour = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True,
                                      help_text="Fuel consumption per engine hour")
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['product_type']),
            models.Index(fields=['entry_source']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['created_at']),
        ]
        # Deduplication constraint
        constraints = [
            models.UniqueConstraint(
                fields=['asset', 'timestamp', 'volume', 'total_cost'],
                name='unique_fuel_transaction'
            )
        ]
    
    def __str__(self):
        return f"{self.asset.asset_id} - {self.volume} {self.unit} {self.product_type} on {self.timestamp.date()}"
    
    def save(self, *args, **kwargs):
        # Calculate total_cost from unit_price if missing
        if self.unit_price and not self.total_cost:
            self.total_cost = self.volume * self.unit_price
        elif self.total_cost and not self.unit_price:
            self.unit_price = self.total_cost / self.volume if self.volume > 0 else Decimal('0')
        
        # Calculate efficiency metrics
        self._calculate_efficiency_metrics()
        
        super().save(*args, **kwargs)
    
    def _calculate_efficiency_metrics(self):
        """Calculate MPG, cost per mile, and fuel per hour"""
        if not self.odometer:
            return
        
        # Find the previous fuel transaction with odometer reading
        previous_txn = FuelTransaction.objects.filter(
            asset=self.asset,
            timestamp__lt=self.timestamp,
            odometer__isnull=False
        ).order_by('-timestamp').first()
        
        if previous_txn and previous_txn.odometer:
            self.distance_delta = self.odometer - previous_txn.odometer
            
            if self.distance_delta > 0:
                # Calculate MPG (skip DEF as it's not fuel for propulsion)
                if self.product_type != 'def':
                    if self.unit == 'gal':
                        self.mpg = self.distance_delta / self.volume
                    elif self.unit == 'L':
                        # Convert liters to gallons for MPG calculation
                        gallons = self.volume / Decimal('3.78541')
                        self.mpg = self.distance_delta / gallons
                    elif self.unit == 'kWh':
                        # Calculate MPGe (miles per gallon equivalent)
                        # 1 gallon gasoline = 33.7 kWh
                        gallon_equivalent = self.volume / Decimal('33.7')
                        self.mpg = self.distance_delta / gallon_equivalent
                
                # Calculate cost per mile
                if self.total_cost:
                    self.cost_per_mile = self.total_cost / self.distance_delta
        
        # Calculate fuel per hour if engine hours available
        if self.engine_hours:
            previous_hours_txn = FuelTransaction.objects.filter(
                asset=self.asset,
                timestamp__lt=self.timestamp,
                engine_hours__isnull=False
            ).order_by('-timestamp').first()
            
            if previous_hours_txn and previous_hours_txn.engine_hours:
                hours_delta = self.engine_hours - previous_hours_txn.engine_hours
                if hours_delta > 0:
                    self.fuel_per_hour = self.volume / hours_delta
    
    @property
    def normalized_volume_gallons(self):
        """Convert volume to gallons for consistent reporting"""
        if self.unit == 'gal':
            return self.volume
        elif self.unit == 'L':
            return self.volume / Decimal('3.78541')
        elif self.unit == 'kWh':
            return self.volume / Decimal('33.7')  # kWh to gallon equivalent
        return self.volume
    
    @property
    def is_anomaly_candidate(self):
        """Flag potential anomalies for review"""
        anomalies = []
        
        # Check for odometer rollback
        if self.distance_delta and self.distance_delta < 0:
            anomalies.append('odometer_rollback')
        
        # Check for unusually low MPG (if we have baseline)
        if self.mpg and self.mpg < 5:  # Configurable threshold
            anomalies.append('low_mpg')
        
        # Check for unusually high unit price
        if self.unit_price and self.unit_price > 10:  # $10/gallon threshold
            anomalies.append('high_price')
        
        return anomalies


class FuelCard(models.Model):
    """Fuel cards for integration (Phase 2)"""
    PROVIDER_CHOICES = [
        ('wex', 'WEX'),
        ('voyager', 'Voyager'),
        ('comdata', 'Comdata'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('lost', 'Lost/Stolen'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    card_last4 = models.CharField(max_length=4, validators=[RegexValidator(r'^\d{4}$')])
    assigned_asset = models.ForeignKey('assets.Asset', on_delete=models.SET_NULL, 
                                     blank=True, null=True, related_name='fuel_cards')
    pin_policy = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    external_id = models.CharField(max_length=100, help_text="Provider's card identifier")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['provider', 'card_last4']
        unique_together = ['provider', 'external_id']
    
    def __str__(self):
        return f"{self.provider.upper()} ****{self.card_last4}"


class FuelAlert(models.Model):
    """Fuel-related alerts and anomalies"""
    ALERT_TYPE_CHOICES = [
        ('low_mpg', 'Low MPG'),
        ('odometer_rollback', 'Odometer Rollback'),
        ('high_price', 'High Unit Price'),
        ('missing_odometer', 'Missing Odometer'),
        ('duplicate_transaction', 'Possible Duplicate'),
        ('unusual_volume', 'Unusual Volume'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Related objects
    asset = models.ForeignKey('assets.Asset', on_delete=models.CASCADE, related_name='fuel_alerts')
    transaction = models.ForeignKey(FuelTransaction, on_delete=models.CASCADE, 
                                  related_name='alerts', blank=True, null=True)
    
    # Alert details
    title = models.CharField(max_length=200)
    description = models.TextField()
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    actual_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Resolution
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='fuel_alerts_resolved')
    resolved_at = models.DateTimeField(blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['asset', 'status']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.alert_type}: {self.asset.asset_id} - {self.title}"


class UnitsPolicy(models.Model):
    """Global units policy for the organization"""
    DISTANCE_UNIT_CHOICES = [
        ('mi', 'Miles'),
        ('km', 'Kilometers'),
    ]
    
    VOLUME_UNIT_CHOICES = [
        ('gal', 'Gallons'),
        ('L', 'Liters'),
    ]
    
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('CAD', 'Canadian Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    distance_unit = models.CharField(max_length=5, choices=DISTANCE_UNIT_CHOICES, default='mi')
    volume_unit = models.CharField(max_length=5, choices=VOLUME_UNIT_CHOICES, default='gal')
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='USD')
    
    # Thresholds for alerts
    low_mpg_threshold_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('25.00'),
                                                  help_text="Alert if MPG drops by this percentage")
    high_price_percentile = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('95.00'),
                                               help_text="Alert if price exceeds this percentile")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Units Policy"
        verbose_name_plural = "Units Policies"
    
    def __str__(self):
        return f"Units: {self.distance_unit}/{self.volume_unit} ({self.currency})"