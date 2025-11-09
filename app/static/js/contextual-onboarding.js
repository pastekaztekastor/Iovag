/**
 * Contextual Onboarding System for Iovag
 * Shows guided tours for recipes, menus, and shopping lists
 */

class ContextualOnboarding {
    constructor(section, steps) {
        this.section = section;
        this.steps = steps;
        this.currentStep = 0;
        this.overlay = null;
        this.tooltip = null;
        this.highlightedElement = null;
    }

    /**
     * Start the onboarding tour
     */
    start() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'onboarding-overlay';
        document.body.appendChild(this.overlay);

        // Create tooltip
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'onboarding-tooltip';
        document.body.appendChild(this.tooltip);

        // Show first step
        this.showStep(0);

        // Activate overlay
        setTimeout(() => {
            this.overlay.classList.add('active');
        }, 100);
    }

    /**
     * Show a specific step
     */
    showStep(stepIndex) {
        if (stepIndex < 0 || stepIndex >= this.steps.length) return;

        this.currentStep = stepIndex;
        const step = this.steps[stepIndex];

        // Remove previous highlight
        if (this.highlightedElement) {
            this.highlightedElement.classList.remove('onboarding-highlight');
        }

        // Find and highlight target element
        const targetElement = document.querySelector(step.target);
        if (targetElement) {
            targetElement.classList.add('onboarding-highlight');
            this.highlightedElement = targetElement;

            // Position tooltip
            this.positionTooltip(targetElement, step.position || 'bottom');

            // Scroll to element
            targetElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // Update tooltip content
        this.updateTooltipContent(step);

        // Show tooltip
        this.tooltip.classList.add('active');
    }

    /**
     * Position the tooltip relative to the target element
     */
    positionTooltip(targetElement, position) {
        const rect = targetElement.getBoundingClientRect();
        const tooltipWidth = 400;
        const tooltipHeight = this.tooltip.offsetHeight || 200;
        const spacing = 20;

        this.tooltip.setAttribute('data-position', position);

        let top, left;

        switch (position) {
            case 'top':
                top = rect.top - tooltipHeight - spacing;
                left = rect.left + (rect.width / 2) - (tooltipWidth / 2);
                break;
            case 'bottom':
                top = rect.bottom + spacing;
                left = rect.left + (rect.width / 2) - (tooltipWidth / 2);
                break;
            case 'left':
                top = rect.top + (rect.height / 2) - (tooltipHeight / 2);
                left = rect.left - tooltipWidth - spacing;
                break;
            case 'right':
                top = rect.top + (rect.height / 2) - (tooltipHeight / 2);
                left = rect.right + spacing;
                break;
            default:
                top = rect.bottom + spacing;
                left = rect.left + (rect.width / 2) - (tooltipWidth / 2);
        }

        // Ensure tooltip stays within viewport
        const maxLeft = window.innerWidth - tooltipWidth - 20;
        const maxTop = window.innerHeight - tooltipHeight - 20;

        left = Math.max(20, Math.min(left, maxLeft));
        top = Math.max(20, Math.min(top, maxTop));

        this.tooltip.style.top = top + 'px';
        this.tooltip.style.left = left + 'px';
    }

    /**
     * Update tooltip content
     */
    updateTooltipContent(step) {
        const isLastStep = this.currentStep === this.steps.length - 1;
        const isFirstStep = this.currentStep === 0;

        this.tooltip.innerHTML = `
            <div class="onboarding-tooltip-header">
                <div class="onboarding-tooltip-icon">${step.icon || '💡'}</div>
                <h3 class="onboarding-tooltip-title">${step.title}</h3>
            </div>
            <div class="onboarding-tooltip-content">
                ${step.content}
            </div>
            <div class="onboarding-tooltip-footer">
                <div class="onboarding-progress">
                    ${this.currentStep + 1} / ${this.steps.length}
                </div>
                <div class="onboarding-buttons">
                    <button class="onboarding-btn onboarding-btn-skip" onclick="onboardingInstance.skip()">
                        Passer
                    </button>
                    ${!isFirstStep ? `
                        <button class="onboarding-btn onboarding-btn-prev" onclick="onboardingInstance.prev()">
                            Précédent
                        </button>
                    ` : ''}
                    ${!isLastStep ? `
                        <button class="onboarding-btn onboarding-btn-next" onclick="onboardingInstance.next()">
                            Suivant
                        </button>
                    ` : `
                        <button class="onboarding-btn onboarding-btn-finish" onclick="onboardingInstance.finish()">
                            Terminer
                        </button>
                    `}
                </div>
            </div>
        `;
    }

    /**
     * Go to next step
     */
    next() {
        if (this.currentStep < this.steps.length - 1) {
            this.showStep(this.currentStep + 1);
        }
    }

    /**
     * Go to previous step
     */
    prev() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }

    /**
     * Skip the tour
     */
    skip() {
        this.complete();
    }

    /**
     * Finish the tour
     */
    finish() {
        this.complete();
    }

    /**
     * Complete the tour and clean up
     */
    complete() {
        // Remove highlight
        if (this.highlightedElement) {
            this.highlightedElement.classList.remove('onboarding-highlight');
        }

        // Remove tooltip
        this.tooltip.classList.remove('active');
        setTimeout(() => {
            this.tooltip.remove();
        }, 300);

        // Remove overlay
        this.overlay.classList.remove('active');
        setTimeout(() => {
            this.overlay.remove();
        }, 300);

        // Mark onboarding as completed for this section
        this.markAsCompleted();
    }

    /**
     * Mark onboarding as completed on the server
     */
    markAsCompleted() {
        fetch(`/complete-contextual-onboarding/${this.section}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => {
            if (response.ok) {
                console.log(`Onboarding ${this.section} completed`);
            }
        }).catch(error => {
            console.error('Error marking onboarding as completed:', error);
        });
    }
}

/**
 * Initialize onboarding for a specific section
 * @param {string} section - The section name (recettes, menus, courses)
 * @param {boolean} needsOnboarding - Whether the user needs onboarding
 * @param {array} steps - The onboarding steps
 */
function initOnboarding(section, needsOnboarding, steps) {
    if (!needsOnboarding || !steps || steps.length === 0) {
        return;
    }

    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            startOnboarding(section, steps);
        });
    } else {
        startOnboarding(section, steps);
    }
}

function startOnboarding(section, steps) {
    // Small delay to ensure all elements are rendered
    setTimeout(() => {
        window.onboardingInstance = new ContextualOnboarding(section, steps);
        window.onboardingInstance.start();
    }, 500);
}
