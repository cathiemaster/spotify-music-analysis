/*
    Catherine Master
    Sept 2022
*/

/*
    Create table for tracks 
*/
Create table IF NOT EXISTS track_history (
    played_at timestamp primary key not null ,
    track_id integer not null,
    title text not null,
    album text not null,
    track_link varchar(255) not null,
    primary_artist text not null,
    feat_artist text not null,
    primary_genre varchar(255) not null,
    secondary_genre varchar(255) not null
);

/* alter table tracks add constraint fk_track_id foreign key (track_id) references tracks(track_id); */

/*
    Create table for artists
*/
Create table IF NOT EXISTS artist_history (
    played_at timestamp not null,
    artist_id integer not null,
    artist_name text not null,
    track_id integer not null,
    primary key (played_at, track_id)
);

/* alter table artists add constraint fk_track_id foreign key (track_id) references tracks(track_id); */

/*
    Create table for genres
*/
Create table IF NOT EXISTS genre_history (
    played_at timestamp not null,
    genre_name varchar(255) not null,
    track_id integer not null,
    primary key (played_at, track_id)
);

/* alter table genres add constraint fk_track_id foreign key (track_id) references tracks(track_id); */

/*
    Create table relating artists and genres
*/
Create table IF NOT EXISTS artists_to_genres (
    artist_id serial not null,
    genre_id serial not null,
    primary key (artist_id, genre_id),
    foreign key (artist_id) references artists (artist_id),
    foreign key (genre_id) references genres (genre_id)
);

Create table IF NOT EXISTS artists_to_genres (
    artist_id serial not null,
    genre_id serial not null,
    primary key (artist_id, genre_id)
);

alter table artists_to_genres add constraint fk_artist_id foreign key (artist_id) references artists(artist_id);

alter table artists_to_genres add constraint fk_genre_id foreign key (genre_id) references genres(genre_id);

/*
    Insert data into tracks table
*/
Insert into tracks (track_id, played_at, title, album, track_link)
values (%s,%s,%s,%s,%s)
return track_id;

Insert into artists (artist_name, track_id)
values (%s,%s)
return artist_id;

Insert into genres (genre_name, track_id)
values (%s,%s)
return genre_id;

Insert into artists_to_genres (artist_id, genre_id)
values (%s,%s)
return *;