-- Run this SQL in the Supabase SQL Editor before starting the API.
-- It creates the `agents` table used by the application.

create table if not exists public.agents (
    id uuid primary key,
    agent_name text not null,
    description text,
    status text not null default 'trial' check (status in ('trial', 'paid')),
    is_verified boolean not null default false,
    is_active boolean not null default true,
    created_at timestamptz not null,
    trial_ends_at timestamptz not null
);

-- Optional: enable Row Level Security and add policies for your use case.
-- alter table public.agents enable row level security;
