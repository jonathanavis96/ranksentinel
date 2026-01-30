/**
 * Analytics tracking utility
 * 
 * Provides a consistent interface for tracking events via GTM/GA4 dataLayer.
 * Events are pushed to the dataLayer array which GTM/GA4 consumes.
 * 
 * In development, events are logged to console for debugging.
 */

// Declare global dataLayer type
declare global {
  type DataLayerEvent = {
    event: string;
    [key: string]: unknown;
  };

  interface Window {
    dataLayer: DataLayerEvent[];
  }
}

interface EventProperties {
  [key: string]: string | number | boolean | undefined;
}

/**
 * Track an analytics event
 * 
 * @param eventName - Name of the event (e.g., 'cta_get_sample_report_click')
 * @param properties - Optional event properties
 * 
 * @example
 * trackEvent('lead_submit', { 
 *   form_type: 'sample_report',
 *   url_provided: true 
 * });
 */
export function trackEvent(eventName: string, properties: EventProperties = {}) {
  // Initialize dataLayer if it doesn't exist
  if (typeof window !== 'undefined') {
    window.dataLayer = window.dataLayer || [];
    
    // Push event to dataLayer
    const eventData = {
      event: eventName,
      ...properties,
    };
    
    window.dataLayer.push(eventData);
    
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log('[Analytics]', eventName, properties);
    }
  }
}
