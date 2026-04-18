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

GENERAL_LEGAL_NOTICE_TEMPLATE = """
LEGAL NOTICE

BY REGISTERED A.D./SPEED POST

From: {sender_name}
Address: {sender_address}

To: {receiver_name}
Address: {receiver_address}

Date: {date}/{month}/{year}

Subject: {subject}

Dear Sir/Madam,

Under instructions from and on behalf of my client, Mr./Ms. {sender_name}, 
I hereby serve upon you the following Legal Notice:

1. That my client states as follows:
{grievance_details}

2. That despite repeated verbal and written requests, you have failed to 
address the above matter, causing my client significant hardship and 
financial/emotional damage.

3. That my client hereby demands the following:
{demand_details}

4. That you are hereby called upon to comply with the above demand within 
15 (Fifteen) days of receipt of this notice, failing which my client shall 
be compelled to initiate appropriate civil and/or criminal proceedings 
against you at your own risk, cost, and consequence.

This notice is issued without prejudice to any other rights and remedies 
available to my client under law.

Issued at {city}.

ADVOCATE / SENDER: ____________________
"""

WILL_TEMPLATE = """
LAST WILL AND TESTAMENT

I, {testator_name}, S/o D/o {parent_name}, aged about {age} years, residing at 
{address}, being of sound mind and disposing memory, do hereby declare this to 
be my Last Will and Testament, revoking all previous Wills and Codicils made by me.

1. I appoint Mr./Ms. {executor_name}, residing at {executor_address}, as the 
Executor of this Will, who shall carry out my wishes as stated herein.

2. DISTRIBUTION OF ASSETS:

{beneficiary_details}

3. I declare that I have made this Will of my own free will, without any 
coercion, undue influence, or fraud by any person.

4. In case any beneficiary named herein predeceases me, the share allotted to 
such person shall be distributed equally among the surviving beneficiaries, 
unless otherwise specified.

IN WITNESS WHEREOF, I have signed this Will at {city} on this {date} day 
of {month}, {year}, in the presence of the following witnesses:

TESTATOR: ____________________

WITNESS 1: ___________________
Name:
Address:

WITNESS 2: ___________________
Name:
Address:
"""

NDA_TEMPLATE = """
NON-DISCLOSURE AGREEMENT (NDA)

THIS NON-DISCLOSURE AGREEMENT is made at {city} on this {date} day of 
{month}, {year},

BETWEEN:

Mr./Ms./M/s. {party_1_name}, having its office/residence at {party_1_address}
(hereinafter referred to as the "Disclosing Party")

AND

Mr./Ms./M/s. {party_2_name}, having its office/residence at {party_2_address}
(hereinafter referred to as the "Receiving Party")

WHEREAS the Disclosing Party possesses certain confidential and proprietary 
information relating to {purpose} and wishes to disclose the same to the 
Receiving Party for the purpose of {purpose}.

NOW, THEREFORE, the parties agree as follows:

1. DEFINITION OF CONFIDENTIAL INFORMATION: "Confidential Information" shall 
include all data, business strategies, financial information, technical know-how, 
trade secrets, client lists, source code, and any other information disclosed 
by the Disclosing Party, whether in writing, orally, or by any other means.

2. OBLIGATIONS: The Receiving Party shall:
   a) Hold all Confidential Information in strict confidence.
   b) Not disclose, publish, or communicate such information to any third party.
   c) Use such information solely for the purpose stated above.
   d) Take all reasonable precautions to prevent unauthorized disclosure.

3. EXCLUSIONS: This agreement does not cover information that:
   a) Is or becomes publicly available without breach of this Agreement.
   b) Was known to the Receiving Party before disclosure.
   c) Is independently developed by the Receiving Party.

4. TERM: This Agreement shall remain in effect for a period of {validity_period} 
from the date of execution. Obligations of confidentiality shall survive 
termination for an additional period of 2 (two) years.

5. REMEDIES: The Disclosing Party shall be entitled to seek injunctive relief 
and damages in the event of any breach of this Agreement.

6. GOVERNING LAW: This Agreement shall be governed by the laws of India. 
Disputes shall be subject to the exclusive jurisdiction of the courts at {city}.

IN WITNESS WHEREOF, the parties have executed this Agreement:

DISCLOSING PARTY: ____________________
RECEIVING PARTY:  ____________________

WITNESS 1: ___________________
WITNESS 2: ___________________
"""

GIFT_DEED_TEMPLATE = """
GIFT DEED

THIS DEED OF GIFT is made at {city} on this {date} day of {month}, {year},

BY:
Mr./Ms. {donor_name}, S/o D/o {donor_parent}, aged about {donor_age} years, 
residing at {donor_address}
(hereinafter referred to as the "DONOR")

IN FAVOUR OF:
Mr./Ms. {donee_name}, S/o D/o {donee_parent}, aged about {donee_age} years, 
residing at {donee_address}
(hereinafter referred to as the "DONEE")

Relationship between Donor and Donee: {relationship}

WHEREAS the Donor is the absolute and lawful owner of the following property/assets:

{gift_description}

AND WHEREAS the Donor, out of natural love and affection for the Donee, 
desires to gift the above-described property/assets to the Donee absolutely 
and unconditionally.

NOW THIS DEED WITNESSETH:

1. That the Donor hereby gifts, grants, and transfers the above-described 
property/assets to the Donee absolutely, forever, and without any consideration.

2. That the Donee has accepted this gift and shall henceforth be the absolute 
owner of the said property/assets.

3. That the Donor has delivered or shall deliver possession of the said 
property/assets to the Donee.

4. That the Donor shall have no claim, right, or interest whatsoever over 
the said property/assets after the execution of this Deed.

IN WITNESS WHEREOF, the Donor and Donee have signed this Deed:

DONOR:  ____________________
DONEE:  ____________________

WITNESS 1: ___________________
WITNESS 2: ___________________
"""

EMPLOYMENT_CONTRACT_TEMPLATE = """
EMPLOYMENT CONTRACT

THIS EMPLOYMENT AGREEMENT is made at {city} on this {date} day of {month}, {year},

BETWEEN:
M/s. {employer_name}, having its registered office at {employer_address}
(hereinafter referred to as the "Employer")

AND:
Mr./Ms. {employee_name}, S/o D/o {employee_parent}, residing at {employee_address}
(hereinafter referred to as the "Employee")

The Employer hereby appoints the Employee on the following terms and conditions:

1. DESIGNATION: The Employee shall be employed as {designation}.

2. COMMENCEMENT: This employment shall commence from {start_date}.

3. COMPENSATION:
   a) Basic Salary: INR {salary} per month.
   b) Additional benefits as per the company's prevailing policies.

4. WORKING HOURS: The Employee shall work {working_hours} hours per week, 
as per the regular schedule of the Employer.

5. PROBATION: The Employee shall serve a probation period of {probation_period}, 
during which employment may be terminated by either party with {notice_period_probation} notice.

6. NOTICE PERIOD: After confirmation, either party may terminate this 
employment by giving {notice_period} written notice.

7. CONFIDENTIALITY: The Employee agrees to maintain strict confidentiality 
regarding all proprietary information, trade secrets, and business operations 
of the Employer during and after the term of employment.

8. NON-COMPETE: The Employee shall not engage in any business or employment 
that directly competes with the Employer for a period of {non_compete_period} 
after termination.

9. TERMINATION: The Employer reserves the right to terminate employment 
immediately for misconduct, breach of contract, or poor performance after 
due process.

10. GOVERNING LAW: This Agreement shall be governed by the laws of India 
and subject to the jurisdiction of courts at {city}.

IN WITNESS WHEREOF, the parties have executed this Agreement:

EMPLOYER:  ____________________
(Authorized Signatory)

EMPLOYEE:  ____________________

WITNESS 1: ___________________
WITNESS 2: ___________________
"""

templates_library = {
    "rent_agreement": RENT_AGREEMENT_TEMPLATE,
    "affidavit": GENERAL_AFFIDAVIT_TEMPLATE,
    "poa": SPECIAL_POA_TEMPLATE,
    "legal_notice_138": LEGAL_NOTICE_138_TEMPLATE,
    "legal_notice": GENERAL_LEGAL_NOTICE_TEMPLATE,
    "will": WILL_TEMPLATE,
    "nda": NDA_TEMPLATE,
    "gift_deed": GIFT_DEED_TEMPLATE,
    "employment_contract": EMPLOYMENT_CONTRACT_TEMPLATE
}

