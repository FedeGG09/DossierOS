create extension if not exists pgcrypto;
create extension if not exists vector;

create table if not exists reglas_ue (
    id uuid primary key default gen_random_uuid(),
    regulation_code text not null,
    regulation_name text not null,
    article_ref text not null,
    article_title text,
    rule_type text not null,
    market text not null default 'EU',
    scope_tags jsonb not null default '[]'::jsonb,
    status text not null default 'active',
    effective_from date,
    effective_to date,
    source_url text,
    source_hash text,
    title text not null,
    text_content text not null,
    chunk_content text,
    numeric_limit numeric,
    unit text,
    prohibited_terms jsonb not null default '[]'::jsonb,
    metadata jsonb not null default '{}'::jsonb,
    embedding vector(384),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists dossiers (
    id uuid primary key default gen_random_uuid(),
    user_id uuid,
    root_dossier_id uuid,
    previous_version_id uuid references dossiers(id) on delete set null,
    superseded_by_version_id uuid references dossiers(id) on delete set null,
    version_number integer not null default 1,
    is_current boolean not null default true,
    product_name text not null,
    active_substance text,
    dosage_form text,
    strength text,
    market text not null,
    dossier_mode text not null,
    status text not null default 'draft',
    source_file_name text,
    source_file_type text,
    source_file_hash text,
    extracted_entities jsonb not null default '{}'::jsonb,
    comparison_result jsonb not null default '{}'::jsonb,
    legal_trace jsonb not null default '{}'::jsonb,
    dossier_payload jsonb not null default '{}'::jsonb,
    metadata jsonb not null default '{}'::jsonb,
    notes text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists dossier_audit_log (
    id uuid primary key default gen_random_uuid(),
    dossier_id uuid not null references dossiers(id) on delete cascade,
    root_dossier_id uuid,
    action text not null,
    changed_by uuid,
    changed_by_email text,
    field_name text,
    old_value jsonb,
    new_value jsonb,
    legal_basis jsonb not null default '[]'::jsonb,
    source_file_name text,
    source_version integer,
    note text,
    created_at timestamptz not null default now()
);

create index if not exists idx_reglas_ue_market on reglas_ue (market);
create index if not exists idx_reglas_ue_rule_type on reglas_ue (rule_type);
create index if not exists idx_reglas_ue_status on reglas_ue (status);
create index if not exists idx_reglas_ue_article_ref on reglas_ue (article_ref);

create index if not exists idx_dossiers_user_id on dossiers (user_id);
create index if not exists idx_dossiers_market on dossiers (market);
create index if not exists idx_dossiers_mode on dossiers (dossier_mode);
create index if not exists idx_dossiers_status on dossiers (status);
create index if not exists idx_dossiers_root_version on dossiers (root_dossier_id, version_number);

create index if not exists idx_dossier_audit_dossier_id on dossier_audit_log (dossier_id);
create index if not exists idx_dossier_audit_root_dossier_id on dossier_audit_log (root_dossier_id);
create index if not exists idx_dossier_audit_created_at on dossier_audit_log (created_at);

alter table dossiers drop constraint if exists ck_dossiers_version_number_positive;
alter table dossiers add constraint ck_dossiers_version_number_positive check (version_number >= 1);

alter table dossiers drop constraint if exists ck_dossiers_status_allowed;
alter table dossiers add constraint ck_dossiers_status_allowed check (status in ('draft', 'under_review', 'approved', 'rejected', 'archived'));

alter table dossiers drop constraint if exists ck_dossiers_mode_allowed;
alter table dossiers add constraint ck_dossiers_mode_allowed check (dossier_mode in ('create', 'update', 'correct'));

create unique index if not exists uq_current_dossier_per_root
on dossiers (root_dossier_id)
where is_current = true;

create or replace function prevent_update_on_final_dossiers()
returns trigger as $$
begin
    if old.status in ('approved', 'archived') then
        raise exception 'Final dossiers are immutable. Create a new version instead.';
    end if;
    new.updated_at := now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_prevent_update_on_final_dossiers on dossiers;
create trigger trg_prevent_update_on_final_dossiers
before update on dossiers
for each row
execute function prevent_update_on_final_dossiers();

create or replace function set_updated_at()
returns trigger as $$
begin
    new.updated_at := now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_reglas_ue_updated_at on reglas_ue;
create trigger trg_reglas_ue_updated_at
before update on reglas_ue
for each row
execute function set_updated_at();

drop trigger if exists trg_dossiers_updated_at on dossiers;
create trigger trg_dossiers_updated_at
before update on dossiers
for each row
execute function set_updated_at();
