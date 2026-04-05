alter table dossiers enable row level security;
alter table reglas_ue enable row level security;
alter table dossier_audit_log enable row level security;

drop policy if exists "Authenticated users can view own dossiers" on dossiers;
drop policy if exists "Authenticated users can insert own dossiers" on dossiers;
drop policy if exists "Authenticated users can update own dossiers" on dossiers;

create policy "Authenticated users can view own dossiers"
on dossiers
for select
to authenticated
using (user_id = auth.uid());

create policy "Authenticated users can insert own dossiers"
on dossiers
for insert
to authenticated
with check (user_id = auth.uid());

create policy "Authenticated users can update own dossiers"
on dossiers
for update
to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

drop policy if exists "Public read reglas" on reglas_ue;
drop policy if exists "No insert reglas" on reglas_ue;

create policy "Public read reglas"
on reglas_ue
for select
using (true);

create policy "No insert reglas"
on reglas_ue
for insert
with check (false);

-- Audit logs: solo el dueño del dossier o admins pueden ver
drop policy if exists "Users can view own audit logs" on dossier_audit_log;
create policy "Users can view own audit logs"
on dossier_audit_log
for select
to authenticated
using (
    exists (
        select 1 from dossiers d
        where d.id = dossier_id and d.user_id = auth.uid()
    )
);


drop policy if exists "Users can insert audit logs" on dossier_audit_log;
create policy "Users can insert audit logs"
on dossier_audit_log
for insert
to authenticated
with check (
    exists (
        select 1 from dossiers d
        where d.id = dossier_id and d.user_id = auth.uid()
    )
);
