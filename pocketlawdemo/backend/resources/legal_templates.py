"""
Pocket Lawyer 2.0 — Professional Indian Legal Templates
High-fidelity, lawyer-vetted document text for the drafting engine.
Includes mandatory clauses for 11-month rent agreements and affidavits.
"""

RENT_AGREEMENT_TEMPLATE = """
RENT AGREEMENT (11-MONTH)

THIS RENT AGREEMENT is made at {city} on this {date} day of {month}, {year}, 
BETWEEN:

Mr./Ms. {landlord_name}, S/o D/o {landlord_parent}, residing at {landlord_address}, 
hereinafter referred to as the "LANDLORD" (which expression shall mean and include 
his/her heirs, successors, legal representatives and assigns) of the ONE PART.

AND

Mr./Ms. {tenant_name}, S/o D/o {tenant_parent}, residing at {tenant_address}, 
hereinafter referred to as the "TENANT" (which expression shall mean and include 
his/her heirs, successors, legal representatives and assigns) of the OTHER PART.

WHEREAS the Landlord is the absolute owner of the residential property situated at 
{property_address} (hereinafter referred to as the "Premises").

The Tenant has approached the Landlord to take the Premises on rent for residential 
purposes, and the Landlord has agreed to let out the same on the following terms:

1. TENURE: This agreement is for a period of 11 (Eleven) months only, commencing 
from {start_date} and ending on {end_date}.

2. RENT: The Tenant shall pay a monthly rent of INR {rent_amount} (Rupees {rent_words} Only) 
on or before the {due_day} day of each English calendar month.

3. SECURITY DEPOSIT: The Tenant has deposited an amount of INR {deposit_amount} 
(Rupees {deposit_words} Only) as an interest-free security deposit. This amount 
shall be refunded at the time of vacating the Premises, subject to adjustments for 
pending bills or damages.

4. MAINTENANCE & UTILITIES: The Tenant shall pay for electricity, water, and 
cooking gas consumption as per the bills received from the authorities. 
Routine maintenance charges shall be borne by the {maintenance_bearer}.

5. USE OF PREMISES: The Premises shall be used strictly for residential purposes 
only. The Tenant shall not sublet or assign the Premises to any third party.

6. TERMINATION: Either party can terminate this agreement by giving {notice_period} 
month(s) prior written notice.

7. LOCK-IN PERIOD: There shall be a lock-in period of {lock_in_months} months, 
during which neither party can terminate the agreement.

IN WITNESS WHEREOF, the parties hereto have signed this agreement in the presence 
of witnesses.

LANDLORD: ____________________
TENANT:   ____________________

WITNESS 1: ___________________
WITNESS 2: ___________________
"""

GENERAL_AFFIDAVIT_TEMPLATE = """
AFFIDAVIT

I, {name}, aged about {age} years, S/o D/o {parent_name}, residing at {address}, 
do hereby solemnly affirm and declare as follows:

1. That I am a citizen of India and a permanent resident of the above-mentioned address.
2. That I am the deponent in this affidavit and am well-acquainted with the facts.
3. That {statement_body}

VERIFICATION:
Verified at {city} on this {date} day of {month}, {year}, that the contents 
of the above affidavit are true and correct to the best of my knowledge and 
belief, and nothing material has been concealed therefrom.

DEPONENT: ____________________
"""

SPECIAL_POA_TEMPLATE = """
SPECIAL POWER OF ATTORNEY

BY THIS POWER OF ATTORNEY, I, {name}, S/o D/o {parent_name}, residing at {address}, 
do hereby appoint Mr./Ms. {attorney_name}, S/o D/o {attorney_parent}, residing at 
{attorney_address}, as my true and lawful Attorney-in-Fact.

My Attorney-in-Fact is authorized to perform the following specific acts on my behalf:
1. To {specific_task_1}
2. To represent me before {authority_name}
3. To sign and execute documents related to {subject_matter}

This Power of Attorney is valid for a period of {validity_period} and shall 
stand revoked thereafter or upon completion of the task.

IN WITNESS WHEREOF, I have set my hand to this Power of Attorney at {city} 
on this {date} day of {month}, {year}.

PRINCIPAL: ____________________
"""

LEGAL_NOTICE_138_TEMPLATE = """
LEGAL NOTICE (SECTION 138 - NI ACT)

BY REGISTERED A.D./SPEED POST

To: {receiver_name}
Address: {receiver_address}

Subject: Legal Notice under Section 138 of the Negotiable Instruments Act, 1881.

Under instructions from my client Mr./Ms. {client_name}, I hereby serve you 
with the following notice:

1. My client is a {client_profession} and had provided {service_provided} to you.
2. Towards the discharge of your liability, you issued a cheque bearing No. {cheque_no} 
dated {cheque_date} for an amount of INR {amount} drawn on {bank_name}.
3. The said cheque, when presented for payment, was returned unpaid by the bank 
with the endorsement "{return_reason}" vide memo dated {memo_date}.
4. I hereby call upon you to pay the said amount of INR {amount} within 15 (Fifteen) 
days of receipt of this notice, failing which my client shall be constrained to 
initiate criminal proceedings against you.

Dated at {city} this {date} day of {month}, {year}.

ADVOCATE
"""

templates_library = {
    "rent_agreement": RENT_AGREEMENT_TEMPLATE,
    "affidavit": GENERAL_AFFIDAVIT_TEMPLATE,
    "poa": SPECIAL_POA_TEMPLATE,
    "notic_138": LEGAL_NOTICE_138_TEMPLATE
}
