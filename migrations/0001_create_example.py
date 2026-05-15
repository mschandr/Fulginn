from yoyo import step

steps = [
    step(
        # forward - runs on `yoyo apply`
        """
        CREATE TABLE IF NOT EXISTS users (
            id uuid primary key default gen_random_uuid(),
            token_hash text not null unique,
            created_at timestamptz not null default now()
        );
        """,
        # rollback 
        """
        DROP TABLE IF EXISTS users;
        """
    ),
]
