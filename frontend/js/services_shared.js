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

        const isDraft = (service.category === 'drafting') || serviceId.startsWith('rent') || ['affidavit', 'poa', 'legal_notice', 'will', 'nda', 'gift_deed', 'employment_contract'].includes(serviceId);
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
            if (type.startsWith('rent_agreement')) setField('landlord_name', user.name);
            if (type === 'affidavit') setField('name', user.name);
            if (type === 'poa') setField('name', user.name);
        }

        // 2. 🧠 AI-Extracted Data (Priority)
        // Rent Agreement specific (Residential & Commercial)
        if (type.startsWith('rent_agreement')) {
            setField('landlord_name', data.landlord_name);
            setField('tenant_name', data.tenant_name);
            setField('rent_amount', data.rent_amount);
            setField('security_deposit', data.security_deposit || data.deposit);
            setField('tenure_months', data.tenure_months || data.period || 11);
            setField('notice_period_days', data.notice_period_days || 30);
            setField('escalation_rate', data.escalation_rate || data.increase_percentage);
            setField('property_address', data.address || data.property_address);
            setField('business_purpose', data.business_purpose || data.purpose);
        }

        // eSign specific
        if (type === 'esign') {
            setField('signerName', data.signer_name || data.name);
            setField('aadhaarLast4', data.aadhaar_last_4);
        }

        // eStamp specific
        if (type === 'estamp') {
            setField('state', data.state);
            setField('value', data.value || data.stamp_value);
            setField('firstParty', data.first_party || data.sender_name);
            setField('secondParty', data.second_party || data.receiver_name);
        }

        // Power of Attorney
        if (type === 'poa') {
            setField('principal_name', data.principal_name || user?.name);
            setField('attorney_name', data.attorney_name);
            setField('powers_context', data.powers_context || data.purpose);
        }

        // Lawyer Appointment
        if (type === 'lawyer_appointment') {
            setField('case_category', data.case_type || data.domain || data.grievance || '');
            setField('brief_context', data.case_reasoning || data.purpose || data.context || '');
        }

        // Legal Notice
        if (type === 'legal_notice') {
            setField('receiver_name', data.receiver_name || data.opposing_party || '');
            setField('demand_amount', data.demand_amount || data.recovery_amount);
            setField('notice_deadline_days', data.notice_deadline_days || 15);
            setField('grievance_details', data.grievance_details || data.case_reasoning || '');
        }

        // Will
        if (type === 'will') {
            setField('testator_name', user ? user.name : '');
            setField('executor_name', data.executor_name || '');
            setField('beneficiary_details', data.beneficiaries || '');
        }

        // NDA
        if (type === 'nda') {
            setField('party_2_name', data.party_2_name || data.other_party || '');
            setField('purpose', data.purpose || data.subject || '');
            setField('secrecy_term_years', data.secrecy_term_years || 3);
        }

        // Gift Deed
        if (type === 'gift_deed') {
            setField('donee_name', data.donee_name || data.recipient || '');
            setField('asset_value', data.asset_value || data.value);
            setField('gift_description', data.gift_description || data.property || '');
        }

        // Employment Contract
        if (type === 'employment_contract') {
            setField('employer_name', data.employer_name || data.company || '');
            setField('salary', data.salary || '');
            setField('notice_period_months', data.notice_period_months || 1);
        }

        // Affidavit
        if (type === 'affidavit') {
            setField('name', user?.name);
            setField('age', data.age);
            setField('father_husband_name', data.father_husband_name);
            setField('statement_body', data.statement_body || data.purpose);
        }
    },

    /**
     * Centralized submission handler for all legal services.
     */
    async handleSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        const serviceId = this.currentServiceId;

        const fileInput = document.getElementById('shared-file-input');
        const file = fileInput ? fileInput.files[0] : null;

        try {
            Utils.showToast("Initiating production workflow...", "info");
            let response;

            if (serviceId === 'esign') {
                if (!file) throw new Error("Please attach a document for eSign.");
                response = await API.requestESign(data.signerName, data.aadhaarLast4, file);
            } 
            else if (serviceId === 'estamp') {
                if (!file) throw new Error("Please attach a document for eStamp.");
                response = await API.requestEStamp(data.state, data.value, file, data.firstParty, data.secondParty);
            }
            else if (serviceId === 'kyc') {
                response = await API.requestKYC('video');
            }
            else {
                // Drafting Service (Will, Rent, NDA, etc.)
                response = await API.requestDraft(serviceId, data);
            }

            if (response.error) throw new Error(response.error);

            Utils.showToast("Success! Service initiated.", "success");
            this.closeModals();
            
            // Refresh parent page if relevant functions exist
            if (typeof loadCombinedList === 'function') loadCombinedList();
            if (typeof loadActiveRequests === 'function') loadActiveRequests();

        } catch (err) {
            Utils.showToast(err.message, "error");
        }
    },

    closeModals() {
        const modal = document.getElementById('service-modal');
        if (modal) modal.classList.add('hidden');
    }
};

// Global hook for the form
function handleSharedServiceSubmit(e) {
    SharedServices.handleSubmit(e);
}

