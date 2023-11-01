from parsel import Selector
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from playwright.sync_api import sync_playwright
import json, re

app = Flask(__name__)
CORS(app)

@app.route('/scrape', methods=['POST', 'OPTIONS'])
def scrape_researchgate_profile():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()

    profileUrl = request.json.get('profileUrl')
    
    if profileUrl is None:
        return jsonify({"error": "Profile URL is missing"}), 400

    profile_data = {
        "basic_info": {},
        "about": {},
        "co_authors": [],
        "publications": []
    }

    with sync_playwright() as p:
        
        browser = p.chromium.launch(headless=True, slow_mo=50)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36")
        page.goto(profileUrl, timeout=0)

        # Use waitForSelector to wait for all desired elements
        page.wait_for_selector('.nova-legacy-e-text--size-xl')
        page.wait_for_selector('.nova-legacy-e-avatar__img')
        page.wait_for_selector('.gtm-institution-item .nova-legacy-e-link--theme-bare')
        page.wait_for_selector('.nova-legacy-v-entity-item__meta-data-item span')
        page.wait_for_selector('.nova-legacy-v-entity-item__info-section-list-item span')
        page.wait_for_selector('.nova-legacy-o-grid--horizontal-align-left .nova-legacy-o-grid__column > div:nth-child(1)')
        page.wait_for_selector('.nova-legacy-o-stack__item .Linkify')
        page.wait_for_selector('.nova-legacy-l-flex__item .nova-legacy-e-badge')
        page.wait_for_selector('.nova-legacy-c-card--spacing-xl .nova-legacy-c-card__body--spacing-inherit .nova-legacy-v-person-list-item')
        page.wait_for_selector('.nova-legacy-v-publication-item__title .nova-legacy-e-link--theme-bare')
        page.wait_for_selector('.nova-legacy-v-publication-item__meta-data-item span')
        page.wait_for_selector('.nova-legacy-v-person-inline-item__fullname')
        page.wait_for_selector('.nova-legacy-e-badge--theme-solid')
        page.wait_for_selector('.nova-legacy-v-publication-item__description')
        page.wait_for_selector('.nova-legacy-c-button-group__item .nova-legacy-c-button')

        selector = Selector(text=page.content())
        
        # Basic information
        profile_data["basic_info"]["name"] = selector.css(".nova-legacy-e-text--size-xl::text").get()
        profile_data["basic_info"]["avatar"] = selector.css(".nova-legacy-e-avatar__img::attr(src)").getall().pop(0)
        profile_data["basic_info"]["institution"] = selector.css(".nova-legacy-o-stack--show-divider .gtm-institution-item .nova-legacy-e-link--theme-bare::text").get()
        profile_data["basic_info"]["department"] = selector.css(".nova-legacy-o-stack--show-divider .gtm-institution-item .nova-legacy-v-entity-item__meta-data-item span").xpath("normalize-space()").get()
        profile_data["basic_info"]["current_position"] = selector.css(".nova-legacy-o-stack--show-divider .nova-legacy-v-entity-item__info-section-list-item span").xpath("normalize-space()").get()
        
        # About information
        numbers = selector.css(".nova-legacy-o-grid--horizontal-align-left .nova-legacy-o-grid__column > div:nth-child(1)::text").getall()
        profile_data["about"]["number_of_publications"] = numbers[0]
        profile_data["about"]["reads"] = numbers[1]
        profile_data["about"]["citations"] = numbers[2]
        profile_data["about"]["introduction"] = selector.css(".nova-legacy-o-stack__item .Linkify").xpath("normalize-space()").get()
        skills = selector.css(".nova-legacy-l-flex__item .nova-legacy-e-badge ::text").getall()
        skills.pop(1)
        skills.pop(0)
        profile_data["about"]["skills"] = skills

        co_authors = selector.css(".nova-legacy-c-card--spacing-xl .nova-legacy-c-card__body--spacing-inherit .nova-legacy-v-person-list-item")
        for i, co_author in enumerate(co_authors):
            if i < 2:  # Limit to the first 2 co-authors
                profile_data["co_authors"].append({
                    "name": co_author.css(".nova-legacy-v-person-list-item__align-content .nova-legacy-e-link::text").get(),
                    "link": co_author.css(".nova-legacy-l-flex__item a::attr(href)").get(),
                    "avatar": co_author.css(".nova-legacy-l-flex__item .lite-page-avatar img::attr(data-src)").get(),
                    "current_institution": co_author.css(".nova-legacy-v-person-list-item__align-content li").xpath("normalize-space()").get()
                })
                
        publications = selector.css("#publications+ .nova-legacy-c-card--elevation-1-above .nova-legacy-o-stack__item")

        for i, publication in enumerate(publications):
            if i < 2:
                profile_data["publications"].append({
                    "title": publication.css(".nova-legacy-v-publication-item__title .nova-legacy-e-link--theme-bare::text").get(),
                    "date_published": publication.css(".nova-legacy-v-publication-item__meta-data-item span::text").get(),
                    "authors": publication.css(".nova-legacy-v-person-inline-item__fullname::text").getall(),
                    "publication_type": publication.css(".nova-legacy-e-badge--theme-solid::text").get(),
                    "description": publication.css(".nova-legacy-v-publication-item__description::text").get(),
                    "publication_link": publication.css(".nova-legacy-c-button-group__item .nova-legacy-c-button::attr(href)").get(),
                })

        browser.close()

    return _corsify_actual_response(jsonify(profile_data))

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)