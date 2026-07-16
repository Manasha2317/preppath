# app/resume/skills_data.py
# Curated dictionary of 200+ technical skills organized by category.
# spaCy's PhraseMatcher uses this to detect skills in resume text.
# Why a dictionary instead of a trained ML model?
# Training custom NER needs thousands of labeled resumes.
# A curated dictionary works out of the box and is easy to extend.

SKILLS_DB = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C", "C#",
        "Go", "Rust", "Kotlin", "Swift", "Ruby", "PHP", "R", "Scala",
        "Dart", "MATLAB", "Perl", "Shell", "Bash", "SQL"
    ],
    "Web Frameworks": [
        "React", "Angular", "Vue", "Next.js", "Nuxt", "Svelte",
        "FastAPI", "Django", "Flask", "Express", "Node.js", "Spring Boot",
        "ASP.NET", "Laravel", "Ruby on Rails", "jQuery", "Bootstrap",
        "TailwindCSS", "Material UI", "Redux", "Zustand"
    ],
    "AI/ML": [
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
        "Keras", "Scikit-learn", "OpenCV", "NLP", "Computer Vision",
        "LangChain", "LangGraph", "Hugging Face", "Transformers",
        "GPT", "Gemini", "LLM", "RAG", "Vector Database", "ChromaDB",
        "Pinecone", "FAISS", "spaCy", "NLTK", "Pandas", "NumPy",
        "Matplotlib", "Seaborn", "XGBoost", "Neural Networks", "CNN",
        "RNN", "LSTM", "Reinforcement Learning", "Fine-tuning",
        "Prompt Engineering", "MLOps", "Whisper", "Stable Diffusion"
    ],
    "Databases": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis",
        "Firebase", "DynamoDB", "Cassandra", "Oracle", "Elasticsearch",
        "Supabase", "Neo4j", "SQLAlchemy"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes",
        "CI/CD", "Jenkins", "GitHub Actions", "Terraform", "Linux",
        "Nginx", "Vercel", "Netlify", "Render", "Railway", "Heroku",
        "Lambda", "EC2", "S3", "CloudFormation", "Ansible"
    ],
    "Mobile": [
        "React Native", "Flutter", "Android", "iOS", "Xamarin",
        "SwiftUI", "Jetpack Compose", "PWA"
    ],
    "Tools & Practices": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Agile",
        "Scrum", "REST API", "GraphQL", "Microservices", "WebSocket",
        "gRPC", "OAuth", "JWT", "Postman", "Swagger", "Figma",
        "System Design", "Data Structures", "Algorithms", "DSA",
        "OOP", "Design Patterns", "Unit Testing", "Pytest", "Jest",
        "TDD", "WebRTC", "Kafka", "RabbitMQ"
    ],
    "Data & Analytics": [
        "Data Analysis", "Data Science", "Power BI", "Tableau",
        "Excel", "ETL", "Data Engineering", "Spark", "Hadoop",
        "Airflow", "dbt", "Snowflake", "BigQuery"
    ]
}

# Flatten for quick lookups: skill name -> category
SKILL_TO_CATEGORY = {}
for category, skills in SKILLS_DB.items():
    for skill in skills:
        SKILL_TO_CATEGORY[skill.lower()] = category

# All skill names as a flat list (for PhraseMatcher patterns)
ALL_SKILLS = [skill for skills in SKILLS_DB.values() for skill in skills]

# Company skill requirements — used for keyword gap analysis
# and company readiness matching on the dashboard
COMPANY_REQUIREMENTS = {
    "Amazon": ["DSA", "System Design", "Java", "Python", "AWS",
               "Microservices", "SQL", "Data Structures", "Algorithms", "OOP"],
    "Google": ["DSA", "System Design", "Python", "C++", "Algorithms",
               "Machine Learning", "Distributed Systems", "SQL", "Go", "Data Structures"],
    "Microsoft": ["DSA", "C#", "Azure", "System Design", "SQL",
                  "REST API", "OOP", "Python", "Data Structures", "Algorithms"],
    "Flipkart": ["DSA", "Java", "System Design", "Microservices",
                 "SQL", "Kafka", "Data Structures", "Algorithms", "Spring Boot", "OOP"],
    "Zerodha": ["Python", "Go", "SQL", "REST API", "System Design",
                "Redis", "PostgreSQL", "Linux", "Data Structures", "Algorithms"],
    "Zoho": ["Java", "JavaScript", "SQL", "OOP", "REST API",
             "DSA", "MySQL", "Spring Boot", "Data Structures", "Algorithms"],
    "TCS": ["Java", "Python", "SQL", "OOP", "Agile",
            "REST API", "JavaScript", "Data Structures", "Git", "Linux"],
    "Infosys": ["Java", "Python", "SQL", "OOP", "Agile",
                "JavaScript", "REST API", "Data Structures", "Git", "Spring Boot"],
    "default": ["DSA", "Python", "SQL", "System Design", "REST API",
                "Git", "OOP", "Data Structures", "Algorithms", "JavaScript"]
}