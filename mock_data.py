"""
mock_data.py
Generates ~2,500 realistic benchmark publication records for KBCNMU
(Kavayitri Bahinabai Chaudhari North Maharashtra University, Jalgaon) for offline/fallback mode.
"""

import random
from datetime import datetime

# KBCNMU Schools and Departments
KBCNMU_DEPARTMENTS = [
    "School of Chemical Sciences",
    "School of Life Sciences",
    "School of Physical Sciences",
    "School of Mathematical Sciences",
    "School of Computer Sciences",
    "School of Environmental & Earth Sciences",
    "School of Engineering & Technology",
    "School of Pharmacy",
    "School of Management Studies",
    "School of Social Sciences",
    "School of Languages & Literature",
]

# KBCNMU Prominent Faculty & Researcher Names (for realistic simulation)
FACULTY_NAMES = [
    "P. P. Mahulikar", "R. S. Bendre", "D. H. More", "D. S. Dalal", "D. K. Gaikwad",
    "S. T. Ingle", "L. A. Patil", "J. B. Naik", "G. K. Patnaik", "R. L. Shinde",
    "A. M. Patil", "V. R. Rathod", "S. R. Patrikar", "M. P. Patil", "S. S. Ghosh",
    "R. Z. Sayyed", "U. D. Patil", "B. L. Chaudhari", "A. B. Chaudhari", "K. B. Patil",
    "S. B. Attarde", "P. R. Puranik", "A. S. Goje", "S. N. Bharambe", "C. S. Kapoor",
    "V. L. Maheshwari", "H. A. Rajole", "M. D. Pawar", "S. K. Omkar", "P. V. Ramaiah"
]

COLLABORATING_COUNTRIES = [
    "India", "United States", "South Korea", "Germany", "Japan",
    "United Kingdom", "Saudi Arabia", "Taiwan", "Malaysia", "Australia",
    "South Africa", "France", "Italy", "China", "Canada"
]

INDUSTRY_AFFILIATIONS = [
    "Lupin Pharmaceuticals Ltd.", "Reliance Industries R&D", "Cipla R&D Centre",
    "BASF India Ltd.", "Sun Pharmaceutical Industries", "UPL Limited",
    "Pidilite Industries", "Dr. Reddy's Laboratories", "Aarti Industries"
]

JOURNALS_BY_DEPT = {
    "School of Chemical Sciences": [
        ("ACS Applied Materials & Interfaces", "Q1", 14.2, 2.35),
        ("RSC Advances", "Q2", 4.8, 0.85),
        ("Journal of Hazardous Materials", "Q1", 16.5, 3.10),
        ("Tetrahedron Letters", "Q3", 2.4, 0.52),
        ("Spectrochimica Acta Part A", "Q1", 6.2, 1.05),
        ("Synthetic Communications", "Q4", 1.8, 0.38),
        ("Journal of Molecular Liquids", "Q1", 7.4, 1.25),
        ("Polymer Bulletin", "Q3", 3.1, 0.58),
    ],
    "School of Life Sciences": [
        ("Bioresource Technology", "Q1", 15.8, 2.95),
        ("Applied Microbiology and Biotechnology", "Q1", 6.8, 1.35),
        ("Journal of Environmental Management", "Q1", 9.8, 1.85),
        ("Process Biochemistry", "Q2", 5.2, 0.98),
        ("3 Biotech", "Q3", 3.2, 0.61),
        ("Microbial Pathogenesis", "Q2", 4.1, 0.82),
        ("Current Microbiology", "Q3", 2.6, 0.49),
    ],
    "School of Physical Sciences": [
        ("Applied Surface Science", "Q1", 8.4, 1.55),
        ("Sensors and Actuators B: Chemical", "Q1", 11.2, 2.10),
        ("Materials Science in Semiconductor Processing", "Q2", 5.4, 0.92),
        ("Journal of Alloys and Compounds", "Q1", 7.2, 1.38),
        ("Optics & Laser Technology", "Q2", 4.9, 0.89),
        ("Ceramics International", "Q1", 6.5, 1.15),
        ("Journal of Applied Physics", "Q2", 3.8, 0.76),
    ],
    "School of Mathematical Sciences": [
        ("Applied Mathematics and Computation", "Q1", 5.6, 1.12),
        ("Journal of Computational and Applied Mathematics", "Q2", 3.9, 0.84),
        ("Communications in Statistics - Theory and Methods", "Q3", 1.8, 0.42),
        ("Fuzzy Sets and Systems", "Q1", 6.2, 1.45),
        ("Soft Computing", "Q2", 4.2, 0.78),
    ],
    "School of Computer Sciences": [
        ("IEEE Access", "Q1", 4.9, 0.98),
        ("Expert Systems with Applications", "Q1", 12.5, 2.45),
        ("Pattern Recognition Letters", "Q2", 5.8, 1.15),
        ("Computers & Electrical Engineering", "Q2", 4.6, 0.88),
        ("Multimedia Tools and Applications", "Q2", 3.8, 0.72),
        ("Journal of King Saud University - Computer and Information Sciences", "Q1", 7.8, 1.62),
    ],
    "School of Environmental & Earth Sciences": [
        ("Environmental Science and Pollution Research", "Q2", 5.8, 1.05),
        ("Chemosphere", "Q1", 10.4, 1.95),
        ("Science of The Total Environment", "Q1", 11.8, 2.30),
        ("Environmental Geochemistry and Health", "Q2", 4.5, 0.86),
        ("Groundwater for Sustainable Development", "Q2", 5.2, 0.94),
    ],
    "School of Engineering & Technology": [
        ("Journal of Applied Polymer Science", "Q2", 3.8, 0.72),
        ("Chemical Engineering Journal", "Q1", 17.2, 3.25),
        ("Desalination", "Q1", 12.4, 2.40),
        ("Materials Today: Proceedings", "Q3", 2.2, 0.45),
        ("International Journal of Chemical Reactor Engineering", "Q4", 1.6, 0.35),
    ],
    "School of Pharmacy": [
        ("European Journal of Medicinal Chemistry", "Q1", 8.2, 1.68),
        ("International Journal of Pharmaceutics", "Q1", 6.9, 1.35),
        ("Drug Delivery", "Q1", 8.5, 1.72),
        ("Journal of Pharmaceutical Sciences", "Q2", 4.5, 0.91),
        ("Biomedicine & Pharmacotherapy", "Q1", 7.8, 1.48),
    ],
    "School of Management Studies": [
        ("Journal of Business Research", "Q1", 11.5, 2.55),
        ("Benchmarking: An International Journal", "Q2", 4.8, 0.95),
        ("International Journal of Production Economics", "Q1", 12.8, 2.80),
        ("Journal of Cleaner Production", "Q1", 13.2, 2.65),
    ],
    "School of Social Sciences": [
        ("Economic and Political Weekly", "Q3", 1.2, 0.31),
        ("Asian Survey", "Q2", 2.1, 0.52),
        ("Journal of Developing Societies", "Q3", 1.5, 0.38),
    ],
    "School of Languages & Literature": [
        ("Language Sciences", "Q2", 2.4, 0.58),
        ("International Journal of Literary Studies", "Q4", 0.9, 0.21),
    ],
}

TITLE_TEMPLATES = [
    "Synthesis, characterization and catalytic activity of novel {chem} complexes for environmental remediation",
    "Development of eco-friendly {bio} nanocomposites for targeted drug delivery systems",
    "Assessment of heavy metal contamination and health risk in groundwater of {geo} region",
    "Enhanced sensing performance of {mat} thin films towards volatile organic compounds",
    "Optimization of fermentation parameters for microbial production of {bio_prod} using agricultural waste",
    "A deep learning approach for predictive analysis of {comp_topic} using hybrid models",
    "Investigation on structural, optical and magnetic properties of substituted {mat} nanoparticles",
    "Green synthesis of silver nanoparticles using plant extracts of North Maharashtra region and their antimicrobial potential",
    "Sorption kinetics and thermodynamics of reactive dyes onto functionalized {chem} biopolymers",
    "Statistical modeling and performance analysis of {math_topic} in complex network systems",
    "Formulation, in-vitro evaluation and pharmacokinetic study of novel {pharm} nano-emulsion",
    "Impact of industrialization on regional economic growth and sustainable development in Khandesh region",
]


def generate_kbcnmu_mock_data(count: int = 2500) -> list:
    """
    Generate specified number of realistic mock publications for KBCNMU.
    """
    random.seed(42)
    publications = []

    years = list(range(1992, 2027))
    # Weight towards recent years (2015-2026)
    year_weights = [(y - 1990) ** 1.8 for y in years]

    chem_terms = ["Schiff base", "Coumarin derivatives", "Chalcone", "Pyrazole", "Zinc oxide", "Titanium dioxide"]
    bio_terms = ["chitosan", "cellulose", "pectin", "alginate", "curcumin", "neem extract"]
    geo_terms = ["Jalgaon district", "Tapi river basin", "Khandesh region", "North Maharashtra"]
    mat_terms = ["ferrite", "cadmium sulfide", "graphene oxide", "polyaniline", "nickel oxide"]
    bio_prod_terms = ["biosurfactant", "cellulase", "amylase", "bioplastic", "laccase"]
    comp_topic_terms = ["smart agriculture", "medical image segmentation", "IoT sensor telemetry", "crop disease detection"]
    math_topic_terms = ["stochastic queues", "fractional differential equations", "fuzzy topology"]
    pharm_terms = ["curcuminoid", "ciprofloxacin", "glimepiride", "metformin", "naproxen"]

    for i in range(1, count + 1):
        dept = random.choice(KBCNMU_DEPARTMENTS)
        journals = JOURNALS_BY_DEPT.get(dept, JOURNALS_BY_DEPT["School of Chemical Sciences"])
        journal_name, quartile, citescore, sjr = random.choice(journals)

        year = random.choices(years, weights=year_weights, k=1)[0]

        # Generate authors
        num_authors = random.randint(2, 6)
        kbcnmu_authors = random.sample(FACULTY_NAMES, min(num_authors, len(FACULTY_NAMES)))
        primary_author = kbcnmu_authors[0]
        authors_str = ", ".join(kbcnmu_authors)

        # Collaborations
        is_international = random.random() < 0.22  # ~22% international
        is_industry = random.random() < 0.10  # ~10% industry

        countries = ["India"]
        if is_international:
            extra_country = random.choice([c for c in COLLABORATING_COUNTRIES if c != "India"])
            countries.append(extra_country)

        # Citations - follow power law (older papers generally have higher citations)
        age = max(1, 2026 - year + 1)
        base_citations = int(random.expovariate(1.0 / (age * 3.5)))
        citations = min(base_citations, 680)

        # Title creation
        template = random.choice(TITLE_TEMPLATES)
        title = template.format(
            chem=random.choice(chem_terms),
            bio=random.choice(bio_terms),
            geo=random.choice(geo_terms),
            mat=random.choice(mat_terms),
            bio_prod=random.choice(bio_prod_terms),
            comp_topic=random.choice(comp_topic_terms),
            math_topic=random.choice(math_topic_terms),
            pharm=random.choice(pharm_terms),
        )

        scopus_id = f"850{random.randint(10000000, 99999999)}"
        doi = f"10.1016/j.{journal_name[:5].lower().replace(' ', '')}.{year}.{random.randint(100, 999)}"

        pub = {
            "scopus_id": scopus_id,
            "title": title,
            "authors": authors_str,
            "primary_author": primary_author,
            "department": dept,
            "journal": journal_name,
            "year": year,
            "citations": citations,
            "citescore": citescore,
            "sjr": sjr,
            "quartile": quartile,
            "doi": doi,
            "is_international_collab": is_international,
            "is_industry_collab": is_industry,
            "countries": countries,
        }
        publications.append(pub)

    # Sort descending by year and citations
    publications.sort(key=lambda x: (x["year"], x["citations"]), reverse=True)
    return publications


if __name__ == "__main__":
    data = generate_kbcnmu_mock_data(2500)
    print(f"Generated {len(data)} mock publications for KBCNMU.")
    print("Sample record:", data[0])
