import streamlit as st

reviews = next(v for k, v in reviews.items() if k.startswith("employerReviews") and v.get("reviews"))