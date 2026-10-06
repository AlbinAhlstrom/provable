You are a senior product analyst. Decide WHAT KIND OF PRODUCT the pitch asks for, before anyone designs a domain model.

BUSINESS PITCH:
"{business_pitch}"

Classify the pitch literally. Use the product type the pitch itself names ("website", "app", "internal tool", "API", ...). Do not upgrade a simple request into an operations platform, and do not invent back-office administration or workflows the pitch does not ask for.

Product types:
- public_website: content and contact for visitors; the owner publishes information, visitors read it and send enquiries.
- customer_app: accounts and transactions for end customers (ordering, booking, tracking their own items).
- internal_tool: staff-only operations software (queues, assignment, back-office control).
- api_service: a programmatic interface consumed by other software.
- marketplace: two sides (providers and customers) matched through listings.
- game: interactive play with rules and scoring.
- data_pipeline: ingestion, transformation or reporting of data.
- other: none of the above fits.

Respond STRICTLY with a valid JSON object (no markdown, no explanations):
{
  "product_type": "<one of: public_website | customer_app | internal_tool | api_service | marketplace | game | data_pipeline | other>",
  "audience": "<who uses it, in one short phrase>",
  "primary_goal": "<what the product must achieve for that audience, one sentence>",
  "scope_summary": "<one sentence describing what the system consists of>",
  "model_focus": ["<2 to 5 kinds of information or capabilities the domain model must cover for this product>"],
  "out_of_scope": ["<0 to 4 things that must NOT be modelled because the pitch did not ask for them>"],
  "assumptions": ["<0 to 3 assumptions you made where the pitch is ambiguous>"]
}
