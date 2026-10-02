# Inquiry email template

Subject: from `spec.email.subject_template`. `{name}` = apartment name, `{dates}` = e.g. "17 to 22 Feb 2027". Default: "{name}, {dates}, Reservation inquiry".

Body (adapt wording to the spec; plain text, no dashes, short):

```
Hello,

I would like to ask about the availability of {unit} for {adults} adults, check-in {weekday date}, check-out {weekday date} ({nights} nights).

{group description sentence, e.g. "We are a group of six adult friends on a ski trip, arriving from {airport}."} We need {real_beds_required} separate beds ({single beds preferred if set}, no sofa beds if set), ideally spread over several bedrooms, plus {must_haves}.

Could you please confirm:
1. Availability for these exact dates{(our flights are already booked) if strict_dates}.
2. The total price for the {nights} nights, including final cleaning, linen, tourist tax and any other fees.
3. The bed configuration in each bedroom, and whether double beds can be set up as two singles.
4. Walking distance to the nearest ski lift, and parking.

{ONE listing-specific question: the thing you could not verify, e.g. conflicting bed info, which lift, minimum stay, Saturday-to-Saturday rule.}

If the place is available, please let me know how to reserve and what deposit you require.

{extra_notes_for_every_email}

Best regards,
{signer_name}
{gmail_account}
```
