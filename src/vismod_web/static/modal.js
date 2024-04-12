/**
 * This callback type is called `modalCallback` and is displayed as a global symbol.
 * @callback modalCallback
 */

/**
 * Allows display of a pop-up with arbitrary messages
 */
class Modal {
    modalHolder = null;
    onConfirm = null;
    onCancel = () => { };

    constructor() {
        this.createEventHandlers = this.createEventHandlers.bind(this);
        this.showModal = this.showModal.bind(this);
        document.addEventListener("DOMContentLoaded", this.createEventHandlers);
    }

    createEventHandlers() {
        this.modalHolder = document.getElementById("modal");
        if (!this.modalHolder) {
            return;
        }
        this.modalHolder.classList.add("visually-hidden");

        const confirmer = document.getElementById("modal-confirm-button");
        const canceller = document.getElementById("modal-cancel-button");

        confirmer.addEventListener("click", () => {
            this.modalHolder.classList.add("visually-hidden");
            if (this.onConfirm) {
                this.onConfirm();
            }
        });
        canceller.addEventListener("click", () => {
            this.modalHolder.classList.add("visually-hidden");
            this.onCancel();
        });
    }

    /**
     * Shows the modal.
     * @param {string} message 
     * @param {modalCallback} onCancel 
     * @param {modalCallback=} onConfirm 
     * @returns 
     */
    showModal(message, onCancel, onConfirm) {
        if (!onCancel) {
            return;
        }
        if (!onConfirm) {
            this.onConfirm = null;
            document.getElementById("modal-confirm-button").classList.add("visually-hidden");
        } else {
            document.getElementById("modal-confirm-button").classList.remove("visually-hidden");
        }
        document.getElementById("modal-content").innerHTML = message;
        this.modalHolder.classList.remove("visually-hidden");
    }
}

window.modalSingleton = new Modal();