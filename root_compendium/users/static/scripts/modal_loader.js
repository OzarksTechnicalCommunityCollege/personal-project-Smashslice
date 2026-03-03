/**
 * Modal Loader - Dynamically loads modal content from Django views
 */

const ModalLoader = {
    containerId: 'modal-container',

    /**
     * Initialize the modal container if it doesn't exist
     */
    init() {
        if (!document.getElementById(this.containerId)) {
            const container = document.createElement('div');
            container.id = this.containerId;
            document.body.appendChild(container);
        }
    },

    /**
     * Load a modal from a Django URL
     * @param {string} url - The Django URL path to fetch the modal content from
     * @param {Object} options - Optional configuration
     * @param {Function} options.onLoad - Callback after modal is loaded
     * @param {Function} options.onClose - Callback when modal is closed
     * @param {Object} options.fetchOptions - Additional fetch options (headers, method, body, etc.)
     * @returns {Promise<HTMLElement>} - The modal element
     */
    async load(url, options = {}) {
        this.init();

        const container = document.getElementById(this.containerId);
        
        try {
            const fetchOptions = {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                ...options.fetchOptions
            };

            const response = await fetch(url, fetchOptions);
            
            if (!response.ok) {
                throw new Error(`Failed to load modal: ${response.status} ${response.statusText}`);
            }

            const html = await response.text();
            container.innerHTML = html;

            const modal = container.querySelector('.modal');
            if (modal) {
                this.show(modal);
                this.setupCloseHandlers(modal, options.onClose);
                
                if (typeof options.onLoad === 'function') {
                    options.onLoad(modal);
                }

                return modal;
            } else {
                throw new Error('No .modal element found in response');
            }
        } catch (error) {
            console.error('ModalLoader error:', error);
            throw error;
        }
    },

    /**
     * Show the modal
     * @param {HTMLElement} modal - The modal element to show
     */
    show(modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
        document.body.classList.add('modal-open');
    },

    /**
     * Hide and remove the modal
     * @param {HTMLElement} modal - The modal element to hide
     */
    close(modal) {
        modal.classList.add('closing');
        modal.classList.remove('active');
        
        // Wait for animation to complete before removing
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
            
            const container = document.getElementById(this.containerId);
            if (container) {
                container.innerHTML = '';
            }
        }, 300);
    },

    /**
     * Setup close handlers for the modal
     * @param {HTMLElement} modal - The modal element
     * @param {Function} onClose - Optional callback when modal is closed
     */
    setupCloseHandlers(modal, onClose) {
        // Close button handler
        const closeButtons = modal.querySelectorAll('[data-modal-close], .modal-close, .close');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.close(modal);
                if (typeof onClose === 'function') {
                    onClose();
                }
            });
        });

        // Click outside to close (on backdrop)
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.close(modal);
                if (typeof onClose === 'function') {
                    onClose();
                }
            }
        });

        // Escape key to close
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.close(modal);
                if (typeof onClose === 'function') {
                    onClose();
                }
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }
};

// Convenience function for quick loading
function loadModal(url, options = {}) {
    return ModalLoader.load(url, options);
}
