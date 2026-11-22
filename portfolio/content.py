"""Single source of truth for everything shown on the site.

Edit this file to update the portfolio. The templates only *render* this data;
no copy lives in the HTML. Strings support a tiny inline markup: ``**bold**``
(see the ``rich`` template filter in ``portfolio/__init__.py``).
"""

PROFILE = {
    "name": "Sumit Kanchole",
    "first_name": "Sumit",
    "short_name": "Sumit",
    "title": "AI Data Annotator & LLM Evaluator",
    "description": (
        "Sumit Kanchole is an AI Data Annotator and LLM Evaluator based in Indore, India, "
        "working on multimodal data labeling, AI response evaluation and quality assurance, "
        "and also building with the MERN stack."
    ),
    "location": "Indore, Madhya Pradesh",
    "location_short": "Indore, India",
    "timezone": "Asia/Kolkata",
    "email": "kancholesumit@gmail.com",
    "phone": "+919755595354",
    "phone_display": "+91 97555 95354",
    "linkedin": "https://linkedin.com/in/sumitkanchole-mern",
    "linkedin_display": "linkedin.com/in/sumitkanchole-mern",
    "resume_file": "assets/Sumit_Kanchole_Resume.pdf",
    "availability": "Open to annotation & evaluation roles",
}

HERO = {
    "backdrop": "SUMIT KANCHOLE",     # large name across the top of the hero
    "greeting": "Hey, I'm Sumit",
    "headline": ["AI Data Annotation", "& LLM Evaluation"],
    "tags": ["LLM Evaluation", "Data Labeling", "Quality Checks"],   # floating pills around the arch
    "stat": {"label": "AI projects\ndelivered", "value": 15, "suffix": "+"},
    # Animated scene inside the arch: an AI answer gets fact-checked and corrected.
    "eval": {
        "prompt": "When was the Eiffel Tower completed?",
        "before": "It was completed in",
        "wrong": "1887",
        "right": "1889",
        "after": "in Paris.",
        "checks": ["✓ Fact-checked", "✓ Clear"],
        "verdict": "Approved",
        "score": 98,
        "breakdown": [98, 97, 99, 98],   # Text, Image, Audio, Video
    },
}

ABOUT = {
    "statement": "I **review, label and evaluate** the data that trains AI models.",
    "principle": ("Accuracy over speed.", "Consistency at scale."),
    "modalities": [("Aa", "Text"), ("▣", "Image"), ("♪", "Audio"), ("▶", "Video")],
    "domains": ["STEM", "Non-STEM", "Generalist"],
    "values_title": ("Detail-first,", "Guideline-driven"),
    "values": ["Factual accuracy", "Guideline adherence", "Quality checks"],
}

PROJECTS = [
    {
        "name": "SkillHub.com",
        "kicker": "Full-stack · MERN",
        "summary": "Skill-exchange platform with real-time chat, video calls and JWT auth.",
        "stack": ["React", "Node", "Express", "MongoDB", "WebRTC", "Socket.io", "JWT"],
        "url": "https://skillhub-mern-project-frontend.onrender.com",
        "url_display": "skillhub.onrender.com",
        "visual": "skillhub",
    },
    {
        "name": "TaskSpace",
        "kicker": "Full-stack · MERN",
        "summary": "Task & workspace manager with Admin/Member panels, task tracking and JWT auth.",
        "stack": ["React", "Node", "Express", "MongoDB", "JWT"],
        "url": "",  # add the live link here when it's deployed
        "url_display": "taskspace.app",
        "visual": "taskspace",
    },
]

SERVICES = {
    "annotation": {
        "title": "Data Annotation",
        "text": "Text, image, audio and video.",
        "tags": ["Text", "Image", "Audio", "Video", "Labeling", "Validation"],
    },
    "evaluation": {
        "title": "LLM Evaluation",
        "text": "Rating AI responses for accuracy.",
        "rubric": [("Accuracy", 92), ("Instructions", 100), ("Clarity", 80)],
    },
    "qa": {
        "title": "Quality Assurance",
        "text": "Checks that keep data clean.",
        "checks": ["Guideline compliance", "Factual verification", "Consistency review"],
    },
    "development": {
        "title": "Development",
        "text": "MERN stack web apps.",
        "stack": ["React", "Node", "Express", "MongoDB", "Socket.io"],
    },
    "cta": {
        "kicker": "Open to new roles",
        "title": "Let's work together",
    },
}

EXPERIENCE = [
    {
        "role": "Data Annotation Intern",
        "company": "Ethara.AI",
        "start": "Jan 2026",
        "end": "May 2026",
        "location": "Gurgaon, India",
        "headline_value": "15+",
        "headline_unit": "AI projects",
        "featured": True,
        "points": [
            "**15+ annotation & evaluation projects** (STEM, Non-STEM, Generalist)",
            "Labeled image, audio, video and text data",
            "Reviewed AI responses for accuracy",
        ],
    },
    {
        "role": "Software Developer Trainee",
        "company": "Infobeans Foundation",
        "start": "Oct 2024",
        "end": "Oct 2025",
        "location": "Indore, India",
        "headline_value": "1 yr",
        "headline_unit": "ITEP program",
        "featured": False,
        "points": [
            "One-year **ITEP training program**",
            "Git, GitHub, Postman and databases",
            "Team-based projects",
        ],
    },
]

EDUCATION = [
    {"years": "2023 — 2026", "degree": "Bachelor of Computer Applications", "school": "Oriental University, Indore"},
    {"years": "2023", "degree": "Higher Secondary", "school": "Government H.S. School Palia, Indore"},
]

PROCESS = [
    {
        "title": "Read the guideline",
        "text": "Learn the rubric and edge cases first.",
        "icon": "file",
    },
    {
        "title": "Annotate carefully",
        "text": "Label every item to the same standard.",
        "icon": "pen",
    },
    {
        "title": "Verify the facts",
        "text": "Check claims against reliable sources.",
        "icon": "search",
    },
    {
        "title": "QA & justify",
        "text": "Self-review and explain every decision.",
        "icon": "check",
    },
]


SKILLS = [
    {
        "title": "Annotation",
        "tag": "Core",
        "visual": "annotate",
        "items": ["Data Annotation", "Data Labeling", "LLM Evaluation", "Quality Assurance"],
    },
    {
        "title": "Technical Stack",
        "tag": "Build",
        "visual": "code",
        "items": ["HTML", "CSS", "JavaScript", "ReactJS", "NodeJS", "ExpressJS", "MySQL", "MongoDB"],
    },
    {
        "title": "Tools",
        "tag": "Work",
        "visual": "tools",
        "items": ["Git & GitHub", "Postman", "VS Code", "Render", "MySQL Workbench"],
    },
]

NAV = [
    ("about", "About"),
    ("work", "Work"),
    ("services", "Services"),
    ("experience", "Experience"),
    ("skills", "Skills"),
]


def site_context():
    """Everything the templates need, as one dict."""
    return {
        "profile": PROFILE,
        "hero": HERO,
        "about": ABOUT,
        "projects": PROJECTS,
        "services": SERVICES,
        "experience": EXPERIENCE,
        "education": EDUCATION,
        "process": PROCESS,
        "skills": SKILLS,
        "nav": NAV,
    }
