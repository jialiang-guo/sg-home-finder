begin;
create table public.home_members (
  user_id uuid primary key references auth.users(id) on delete cascade
);
create table public.home_decisions (
  listing_key text primary key check (length(listing_key) between 1 and 160),
  decision text not null check (decision in ('keep','reject','reset')),
  updated_at timestamptz not null default now(),
  updated_by uuid references auth.users(id) on delete set null
);
alter table public.home_members enable row level security;
alter table public.home_decisions enable row level security;
revoke all on public.home_members from anon, authenticated;
revoke all on public.home_decisions from anon, authenticated;
grant select on public.home_members to authenticated;
grant select on public.home_decisions to anon, authenticated;
grant insert (listing_key, decision, updated_by), update (listing_key, decision, updated_by) on public.home_decisions to authenticated;
create policy own_membership on public.home_members for select to authenticated using (user_id = (select auth.uid()));
create policy shared_read on public.home_decisions for select to anon, authenticated using (true);
create policy member_insert on public.home_decisions for insert to authenticated with check (
  updated_by = (select auth.uid()) and exists (select 1 from public.home_members where user_id = (select auth.uid()))
);
create policy member_update on public.home_decisions for update to authenticated using (
  exists (select 1 from public.home_members where user_id = (select auth.uid()))
) with check (updated_by = (select auth.uid()) and exists (select 1 from public.home_members where user_id = (select auth.uid())));
create function public.stamp_home_decision() returns trigger language plpgsql set search_path = '' as $$
begin new.updated_at = now(); return new; end $$;
create trigger home_decision_timestamp before update on public.home_decisions for each row execute function public.stamp_home_decision();
commit;
