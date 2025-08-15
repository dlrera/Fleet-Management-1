import { describe, it, expect } from 'vitest'
import { renderWithProviders } from './test-utils'

describe('Test Setup', () => {
  it('should render a basic Vue component', () => {
    const TestComponent = {
      template: '<div data-testid="test">Hello World</div>'
    }
    
    const { getByTestId } = renderWithProviders(TestComponent)
    expect(getByTestId('test')).toHaveTextContent('Hello World')
  })
  
  it('should have Vuetify components available', () => {
    const VuetifyComponent = {
      template: '<v-btn data-testid="vuetify-btn">Click me</v-btn>'
    }
    
    const { getByTestId } = renderWithProviders(VuetifyComponent)
    expect(getByTestId('vuetify-btn')).toBeInTheDocument()
  })
  
  it('should have access to testing utilities', () => {
    expect(typeof renderWithProviders).toBe('function')
  })
})