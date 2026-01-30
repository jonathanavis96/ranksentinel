'use client';

import { useState, useRef, KeyboardEvent } from 'react';

interface FAQItem {
  id: string;
  question: string;
  answer: string;
}

interface FAQAccordionProps {
  items: FAQItem[];
}

export function FAQAccordion({ items }: FAQAccordionProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const buttonRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const handleToggle = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLButtonElement>, index: number) => {
    let targetIndex = index;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        targetIndex = (index + 1) % items.length;
        break;
      case 'ArrowUp':
        e.preventDefault();
        targetIndex = (index - 1 + items.length) % items.length;
        break;
      case 'Home':
        e.preventDefault();
        targetIndex = 0;
        break;
      case 'End':
        e.preventDefault();
        targetIndex = items.length - 1;
        break;
      default:
        return;
    }

    buttonRefs.current[targetIndex]?.focus();
  };

  return (
    <div className="space-y-4">
      {items.map((item, index) => {
        const isExpanded = expandedId === item.id;
        const buttonId = `faq-button-${item.id}`;
        const contentId = `faq-content-${item.id}`;

        return (
          <div key={item.id} className="border border-gray-200 rounded-lg overflow-hidden">
            <h3>
              <button
                ref={(el) => {
                  buttonRefs.current[index] = el;
                }}
                id={buttonId}
                aria-expanded={isExpanded}
                aria-controls={contentId}
                onClick={() => handleToggle(item.id)}
                onKeyDown={(e) => handleKeyDown(e, index)}
                className="w-full flex items-center justify-between px-6 py-4 text-left bg-white hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
              >
                <span className="font-semibold text-gray-900 pr-8">{item.question}</span>
                <svg
                  className={`w-5 h-5 text-gray-500 flex-shrink-0 transition-transform ${
                    isExpanded ? 'transform rotate-180' : ''
                  }`}
                  aria-hidden="true"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </h3>
            <div
              id={contentId}
              role="region"
              aria-labelledby={buttonId}
              hidden={!isExpanded}
              className={`px-6 pb-4 text-gray-700 ${isExpanded ? '' : 'hidden'}`}
            >
              <div className="pt-2">{item.answer}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
