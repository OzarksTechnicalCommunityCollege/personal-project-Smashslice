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

                // Setup form interception for AJAX submission
                this.setupFormHandlers(modal);

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
    },

    /**
     * Setup form handlers for AJAX submission
     * @param {HTMLElement} modal - The modal element
     */
    setupFormHandlers(modal) {
        const forms = modal.querySelectorAll('form[data-modal-form]');
        forms.forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                const url = form.action;
                
                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        },
                        body: formData
                    });
                    
                    const contentType = response.headers.get('content-type');
                    
                    if (contentType && contentType.includes('application/json')) {
                        // JSON response = success
                        const data = await response.json();
                        if (data.success) {
                            this.close(modal);
                            if (data.redirect) {
                                window.location.href = data.redirect;
                            } else {
                                window.location.reload();
                            }
                        }
                    } else {
                        // HTML response = form errors, replace modal content
                        const html = await response.text();
                        const container = document.getElementById(this.containerId);
                        container.innerHTML = html;
                        
                        const newModal = container.querySelector('.modal');
                        if (newModal) {
                            this.show(newModal);
                            this.setupCloseHandlers(newModal);
                            this.setupFormHandlers(newModal);
                        }
                    }
                } catch (error) {
                    console.error('Form submission error:', error);
                }
            });
        });
    },

    /**
     * Auto-initialize click handlers for elements with data-modal-url
     */
    initTriggers() {
        document.querySelectorAll('[data-modal-url]').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                this.load(trigger.dataset.modalUrl);
            });
        });
    }
};

// Convenience function for quick loading
function loadModal(url, options = {}) {
    return ModalLoader.load(url, options);
}

// Auto-init on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    ModalLoader.initTriggers();
});
