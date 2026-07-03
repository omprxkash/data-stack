-- Seed three tenants with notes.
-- After RLS policies are applied, each tenant can only see their own rows.

INSERT INTO tenant_notes (tenant_id, title, body) VALUES
  ('acme',    'Q1 Goals',         'Grow revenue by 15% in Q1.'),
  ('acme',    'Team Offsite',     'Book venue for the March offsite.'),
  ('globex',  'Security Audit',   'Pen test scheduled for February.'),
  ('globex',  'New Hire Onboard', 'Start date confirmed for Jan 20.'),
  ('initech', 'Budget Review',    'CFO meeting set for Jan 30.'),
  ('initech', 'Roadmap Draft',    'Draft the H1 roadmap by end of month.');
