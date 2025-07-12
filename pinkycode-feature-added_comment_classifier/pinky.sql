create database pinky
    with owner pinky;

create table public."user"
(
    id       serial
        constraint user_pk
            primary key,
    login    varchar(64),
    password varchar(64)
);

alter table public."user"
    owner to pinky;

create table public.session
(
    id      varchar(64) not null
        constraint session_pk
            primary key,
    user_id integer     not null
        constraint session_user_id_fk
            references public."user"
            on update cascade on delete cascade
);

alter table public.session
    owner to pinky;

create table public.history
(
    id        serial
        constraint history_pk
            primary key,
    user_id   bigint                              not null
        constraint history_user_id_fk
            references public."user"
            on update cascade on delete cascade,
    time      timestamp default CURRENT_TIMESTAMP not null
        constraint history_pk_2
            unique,
    file_name varchar(255),
    issues    text
);

alter table public.history
    owner to pinky;

