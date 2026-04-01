/**
 * Pocket Lawyer 2.0 — Master App State Controller (Citizen Side)
 * Manages the "Legal Cart" (Current Case), Identity Profile, and Workflow Routing.
 */

const AppState = {
    // 🛒 CASE / CART STATE
    // Each case acts as a cart containing one or more services.
    getCart: function() {
        return JSON.parse(localStorage.getItem('pocket_lawyer_cart') || '{"active_case": null, "services": []}');
    },

    saveCart: function(cart) {
        localStorage.setItem('pocket_lawyer_cart', JSON.stringify(cart));
        // Dispatch event for UI updates
        window.dispatchEvent(new CustomEvent('cartUpdated', { detail: cart }));
    },

    addToCart: function(serviceKey, extractedData = {}, title = null) {
        const cart = this.getCart();
        
        // If no active case, create one based on the first service
        if (!cart.active_case) {
            cart.active_case = {
                id: Date.now(),
                title: title || extractedData.issue || 'New Legal Matter',
                status: 'active'
            };
        }

        // Check for duplicates via "Merge Key" (Service + Party/Issue)
        const mergeKey = `${serviceKey}_${extractedData.opposite_party || 'general'}`;
        const existing = cart.services.find(s => s.merge_key === mergeKey);
        const newId = Date.now() + Math.floor(Math.random() * 1000);

        if (existing) {
            existing.data = { ...existing.data, ...extractedData };
            existing.updated_at = new Date().toISOString();
        } else {
            // Create new service instance in the cart
            cart.services.push({
                instance_id: newId,
                service_key: serviceKey,
                merge_key: mergeKey,
                status: 'pending',
                data: extractedData,
                created_at: new Date().toISOString()
            });
        }

        this.saveCart(cart);
        return { activeCase: cart.active_case, instanceId: existing ? existing.instance_id : newId };
    },

    // 👤 IDENTITY / PROFILE STATE
    getProfile: function() {
        return JSON.parse(localStorage.getItem('pocket_lawyer_profile') || '{}');
    },

    // 🚀 WORKFLOW ROUTING
    // Maps AI 'service_key' to the Guided Workflow Wizard
    startWorkflow: function(serviceKey, instanceId = null) {
        // If no instanceId, it's a "Buy Now" flow (add to cart first)
        if (!instanceId) {
            const cart = this.getCart();
            const instance = cart.services.find(s => s.service_key === serviceKey && s.status === 'pending');
            if (instance) instanceId = instance.instance_id;
        }

        // Redirect to the Wizard with the specific service context
        const url = `workflow.html?service=${serviceKey}${instanceId ? '&instance=' + instanceId : ''}`;
        window.location.href = url;
    },

    getMergedData: function(instanceId) {
        const cart = this.getCart();
        // Use loose equality to handle string/number mismatches from URL params
        const service = cart.services.find(s => s.instance_id == instanceId);
        const profile = this.getProfile();

        if (!service) {
            console.warn('AppState: Service instance not found for ID', instanceId);
            return profile;
        }

        // Priority Mapping: Service Data (AI/User edits) > Profile Data
        return {
            ...profile,
            ...(service.data || {}),
            // Ensure legal names are preserved from profile if not in service
            full_name: (service.data && service.data.full_name) || profile.full_name || '',
            address: (service.data && service.data.address_line) || profile.address_line || ''
        };
    }
};

// Auto-export for browser use
window.AppState = AppState;
