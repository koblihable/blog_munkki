from sqlalchemy import Integer, String, Text, ForeignKey, Boolean, DateTime
from typing import List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin
from extensions import db
import datetime as dt




class User(UserMixin, db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name:Mapped[str] = mapped_column(String(255), nullable=False, default='none')
    last_name:Mapped[str] = mapped_column(String(255), nullable=False, default='none')
    email:Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password:Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin:Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    is_protected: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    profile_pic:Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    date_created:Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now)
    date_updated: Mapped[dt.datetime] = mapped_column(DateTime(),
                                                      nullable=False,
                                                      default=dt.datetime.now,
                                                      onupdate=dt.datetime.now)
    last_logged_in:Mapped[dt.datetime] = mapped_column(DateTime(), nullable=True, default=None)

    # parent relationships
    posts: Mapped[List['BlogPost']] = relationship('BlogPost', back_populates='author')
    comments:Mapped[List['Comment']] = relationship('Comment', back_populates='comment_author')

    @property
    def has_posts(self):
        return bool(self.posts)

    @property
    def has_comments(self):
        return bool(self.comments)


class BlogPost(db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    subtitle:Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    body:Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    date_created:Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now)
    date_updated: Mapped[dt.datetime] = (
        mapped_column(DateTime(), nullable=False, default=dt.datetime.now, onupdate=dt.datetime.now)
    )
    img_url:Mapped[str] = mapped_column(String(255))

    # child relationship
    author_id:Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False)
    author:Mapped['User'] = relationship('User', back_populates='posts')

    # parent relationship
    post_comments:Mapped[List['Comment']] = relationship('Comment', back_populates='parent_post')


class Comment(db.Model):
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    date_created:Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now)
    date_updated: Mapped[dt.datetime] = mapped_column(DateTime(), nullable=False, default=dt.datetime.now)
    text: Mapped[str] = mapped_column(String(255), nullable=False)

    # child relationships
    author_id:Mapped[int] = mapped_column(Integer, ForeignKey(User.id, ondelete="SET NULL"), nullable=True)
    comment_author:Mapped['User'] = relationship('User', back_populates='comments')
    post_id:Mapped[int] = mapped_column(Integer, ForeignKey(BlogPost.id), nullable=False)
    parent_post:Mapped['BlogPost'] = relationship('BlogPost', back_populates='post_comments')

