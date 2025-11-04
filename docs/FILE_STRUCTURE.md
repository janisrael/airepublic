ai-republic/
│
├── backend/                     # Flask / FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py            # Configs: DB, API keys, env
│   │   ├── extensions.py        # DB, Mail, JWT, Cache, Scheduler
│   │   ├── models/              # ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── role_permission.py
│   │   │   ├── subscription.py
│   │   │   ├── provider.py
│   │   │   ├── ai_models.py
│   │   │   ├── minions.py
│   │   │   ├── datasets.py
│   │   │   └── training.py
│   │   │
│   │   ├── schemas/             # Pydantic / Marshmallow schemas
│   │   │   ├── __init__.py
│   │   │   ├── user_schema.py
│   │   │   ├── subscription_schema.py
│   │   │   ├── model_schema.py
│   │   │   └── training_schema.py
│   │   │
│   │   ├── routes/              # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── subscription.py
│   │   │   ├── provider.py
│   │   │   ├── model.py
│   │   │   ├── minion.py
│   │   │   ├── training.py
│   │   │   └── dataset.py
│   │   │
│   │   ├── services/            # Business logic / service layer
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── subscription_service.py
│   │   │   ├── provider_service.py
│   │   │   ├── ai_model_service.py
│   │   │   ├── training_service.py
│   │   │   └── dataset_service.py
│   │   │
│   │   ├── utils/               # Helpers, utils, email, encryption, etc.
│   │   │   ├── __init__.py
│   │   │   ├── email_utils.py
│   │   │   ├── jwt_utils.py
│   │   │   ├── encryption.py
│   │   │   └── logging.py
│   │   │
│   │   ├── jobs/                # Background jobs / schedulers
│   │   │   ├── __init__.py
│   │   │   ├── training_jobs.py
│   │   │   └── provider_usage.py
│   │   │
│   │   └── middlewares/         # Auth, logging, rate-limit, etc.
│   │       ├── __init__.py
│   │       ├── auth_middleware.py
│   │       └── rate_limit.py
│   │
│   ├── main.py                  # App entry point
│   └── requirements.txt
│
├── frontend/                     # Vue.js / React frontend
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   ├── Dashboard/
│   │   │   ├── AIModels/
│   │   │   ├── Minions/
│   │   │   ├── Training/
│   │   │   └── Datasets/
│   │   │
│   │   ├── pages/
│   │   ├── router/
│   │   ├── store/
│   │   ├── services/            # Frontend API service calls
│   │   └── App.vue / main.js
│   └── package.json
│
├── database/                     # DB schema, migrations, seeds
│   ├── migrations/
│   ├── seeds/
│   └── ai_dashboard.db
│
├── docs/                         # Documentation, diagrams, ERDs
│   └── ERD.md
│
├── scripts/                      # CLI scripts / utilities
│   ├── seed_data.py
│   └── generate_report.py
│
├── tests/                        # Unit / Integration tests
│   ├── backend/
│   │   ├── test_auth.py
│   │   ├── test_models.py
│   │   └── test_training.py
│   └── frontend/
│       └── component_tests/
│
├── docker/                       # Docker configs
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── docker-compose.yml
│
└── README.md
