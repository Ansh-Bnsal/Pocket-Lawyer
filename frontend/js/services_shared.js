/**
 * POCKET LAWYER 2.0 — Shared Service Logic
 * Decouples modal handling from individual pages and enables AI-driven pre-filling.
 */

const SharedServices = {
    currentServiceId: null,
    servicesCatalog: [],

    async init() {
        if (this.servicesCatalog.length === 0) {
            this.servicesCatalog = await API.listLegalServices();
        }
    },

    /**
     * Opens the relevant legal service modal and pre-fills it with AI or User data.
     */
    async openServiceModal(serviceId, aiData = null) {
        await this.init();
        this.currentServiceId = serviceId;
        
        const service = this.servicesCatalog.find(s => s.id === serviceId);
        if (!service) {
            Utils.showToast("Service not found in catalog.", "error");
            return;
        }

        const modal = document.getElementById('service-modal');
        if (!modal) {
            console.error("Service modal not found on this page.");
            return;
        }

        const isDraft = serviceId.startsWith('rent') || serviceId.startsWith('affidavit') || serviceId.startsWith('poa');
        document.getElementById('modal-title').innerText = isDraft ? `Draft: ${service.name}` : `Initiate: ${service.name}`;
        modal.classList.remove('hidden');

        // Hide all forms, show relevant one
        document.querySelectorAll('.step-form').forEach(f => f.classList.remove('active'));
        const step = document.getElementById('step-' + serviceId);
        if (step) step.classList.add('active');

        // Document Upload Zone
        const uploadZone = document.getElementById('step-upload');
        if (uploadZone) {
            if (service.require_doc) uploadZone.classList.remove('hidden');
            else uploadZone.classList.add('hidden');
        }

        // 🧠 PRE-FILLING LOGIC (Merging AI data + User Profile)
        const user = API.getUser();
        const form = document.getElementById('service-context-form');
        if (form) {
            this._preFillForm(form, serviceId, aiData, user);
        }

        // Update button text
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerText = isDraft ? 'Generate Professional Draft' : 'Initiate Service';
        }
    },

    _preFillForm(form, type, aiData, user) {
        const data = aiData || {};
        
        // Helper to set field value if it exists and is empty
        const setField = (name, val) => {
            const el = form.querySelector(`[name="${name}"]`);
            if (el && val) el.value = val;
        };

        // 1. Generic User Data (Fallback)
        if (user) {
            if (type === 'esign') setField('signerName', user.name);
            if (type === 'estamp') setField('firstParty', user.name);
            if (type === 'rent_agreement') setField('landlord_name', user.name);
            if (type === 'affidavit') setField('name', user.name);
            if (type === 'poa') setField('name', user.name);
        }

        // 2. 🧠 AI-Extracted Data (Priority)
        // Rent Agreement specific
        if (type === 'rent_agreement') {
            setField('landlord_name', data.landlord_name);
            setField('tenant_name', data.tenant_name);
            setField('rent_amount', data.rent_amount);
            setField('deposit_amount', data.deposit_amount);
            setField('property_address', data.address || data.property_address);
        }

        // eSign specific
        if (type === 'esign') {
            setField('signerName', data.signer_name || data.name);
        }

        // Power of Attorney
        if (type === 'poa') {
            setField('attorney_name', data.attorney_name);
            setField('subject_matter', data.purpose);
        }

        // Lawyer Appointment
        if (type === 'lawyer_appointment') {
            setField('case_category', data.case_type || data.domain || data.grievance || '');
            setField('brief_context', data.case_reasoning || data.purpose || data.context || '');
        }
    }
};
