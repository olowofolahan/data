-- ============================================================================
-- Turf — Supabase schema for OPEN async multiplayer
-- Run this once in your Supabase project: Dashboard > SQL Editor > New query >
-- paste all of this > Run.
--
-- It creates two tables (a leaderboard and a raids inbox) and opens them to the
-- anonymous (public) key so ANY player on the shared game link can post their
-- score and raid. This is trust-based (fine for a fun game): anyone technical
-- could write arbitrary rows. For competitive integrity you'd add Supabase Auth
-- and tie rows to auth.uid(); see the note at the bottom.
-- ============================================================================

-- --- Leaderboard: one row per player (client-generated uuid id) -------------
create table if not exists public.players (
  id          uuid primary key,
  name        text not null default 'Boss',
  level       int  not null default 1,
  rank        text not null default 'Hustler',
  respect     int  not null default 0,
  power       int  not null default 0,
  defense     int  not null default 0,
  districts   int  not null default 0,
  city        text,
  country     text,
  updated_at  timestamptz not null default now()
);
create index if not exists players_respect_idx on public.players (respect desc);

-- --- Raids: an inbox of raids made on a defender ----------------------------
create table if not exists public.raids (
  id            uuid primary key default gen_random_uuid(),
  attacker      uuid,
  attacker_name text,
  defender_id   uuid not null,
  win           boolean not null default false,
  loot          bigint  not null default 0,
  ts            timestamptz not null default now()
);
create index if not exists raids_defender_idx on public.raids (defender_id);

-- --- Row level security: open to the anon (public) key ----------------------
alter table public.players enable row level security;
alter table public.raids   enable row level security;

-- players: everyone may read; anyone may insert/update/delete (open game)
drop policy if exists players_read  on public.players;
drop policy if exists players_write on public.players;
create policy players_read  on public.players for select using (true);
create policy players_write on public.players for all    using (true) with check (true);

-- raids: everyone may read; anyone may insert; anyone may delete (defender
-- clears their processed raids)
drop policy if exists raids_read   on public.raids;
drop policy if exists raids_write  on public.raids;
create policy raids_read  on public.raids for select using (true);
create policy raids_write on public.raids for all    using (true) with check (true);

-- Optional: keep the raids table from growing forever — delete rows older than
-- 30 days. (Run manually now and then, or schedule with pg_cron if enabled.)
-- delete from public.raids where ts < now() - interval '30 days';

-- ============================================================================
-- HARDENING (optional, later): turn on Supabase Auth (anonymous sign-ins are
-- fine), add an `owner uuid default auth.uid()` column to each table, and change
-- the write policies to `using (owner = auth.uid()) with check (owner = auth.uid())`
-- so a player can only change their own rows. Keep the read policies open.
-- ============================================================================
