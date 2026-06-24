from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.core.files.base import ContentFile
import random

from shop.models import Category, Product, Coupon
from blog.models import Post
from core.models import User, Service, Testimonial
from learn.models import Language, Topic
from projects.models import Project

class Command(BaseCommand):
    help = 'Seeds database with premium multi-category ebooks and blog posts.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # 1. Create Superuser if not exists
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser('admin', 'admin@bobbythecoder.in', 'admin123')
            admin_user.is_verified = True
            admin_user.save()
            self.stdout.write("Created Superuser: admin / admin123")

        # 2. Create Categories
        backend_cat, _ = Category.objects.get_or_create(name="Backend Development", slug="backend-development")
        frontend_cat, _ = Category.objects.get_or_create(name="Frontend Development", slug="frontend-development")
        career_cat, _ = Category.objects.get_or_create(name="Career Guides", slug="career-guides")
        system_cat, _ = Category.objects.get_or_create(name="System Design", slug="system-design")

        # Create dummy image content files
        dummy_thumb = ContentFile(b"dummy_image_data", name="thumbnail.jpg")
        dummy_file = ContentFile(b"dummy_digital_file_data", name="product.zip")

        # 3. Create Products
        p1, _ = Product.objects.get_or_create(
            title="Django Scalable Backend Blueprint",
            slug="django-scalable-backend-blueprint",
            category=backend_cat,
            description="Complete reference guide to building scalable, production-ready Django applications. Covers custom middleware, postgreSQL setups, celery task queues, Redis, and Razorpay integrations. Includes sample boilerplate code structures.",
            price=1299.00,
            discount_price=899.00,
            is_free=False,
            difficulty_level="advanced",
            programming_language="django",
            rating=5.0,
            is_featured=True
        )
        if not p1.thumbnail:
            p1.thumbnail.save("p1_thumb.jpg", dummy_thumb)
            p1.file.save("p1_file.zip", dummy_file)
            p1.save()

        p2, _ = Product.objects.get_or_create(
            title="Python Cracking Code Ebook",
            slug="python-cracking-code-ebook",
            category=backend_cat,
            description="Master python foundations, object-oriented programming (OOP), data structures, files parsing, and standard APIs. Written with diagrams, interview patterns, and clean snippets.",
            price=799.00,
            discount_price=499.00,
            is_free=False,
            difficulty_level="beginner",
            programming_language="python",
            rating=4.9,
            is_featured=True
        )
        if not p2.thumbnail:
            p2.thumbnail.save("p2_thumb.jpg", dummy_thumb)
            p2.file.save("p2_file.zip", dummy_file)
            p2.save()

        p3, _ = Product.objects.get_or_create(
            title="React & Next.js SaaS UI Kit",
            slug="react-nextjs-saas-ui-kit",
            category=frontend_cat,
            description="A premium collection of copy-paste TailwindCSS and React components optimized for high-converting SaaS landing pages, forms, and glassmorphic dashboards.",
            price=999.00,
            discount_price=699.00,
            is_free=False,
            difficulty_level="intermediate",
            programming_language="javascript",
            rating=4.8,
            is_featured=False
        )
        if not p3.thumbnail:
            p3.thumbnail.save("p3_thumb.jpg", dummy_thumb)
            p3.file.save("p3_file.zip", dummy_file)
            p3.save()

        p4, _ = Product.objects.get_or_create(
            title="Fullstack Web Developer Career Handbook",
            slug="fullstack-web-developer-career-handbook",
            category=career_cat,
            description="Learn how to structure your developer resume, prepare for coding interview rounds, negotiate salary packages, and find freelance clients.",
            price=499.00,
            discount_price=299.00,
            is_free=False,
            difficulty_level="beginner",
            programming_language="other",
            rating=4.7,
            is_featured=False
        )
        if not p4.thumbnail:
            p4.thumbnail.save("p4_thumb.jpg", dummy_thumb)
            p4.file.save("p4_file.zip", dummy_file)
            p4.save()

        p5, _ = Product.objects.get_or_create(
            title="System Design & REST API Handbook",
            slug="system-design-rest-api-handbook",
            category=system_cat,
            description="A visual reference guide covering microservices, caching layers, load balancers, rate limiters, database sharding, and clean RESTful API standards.",
            price=1499.00,
            discount_price=999.00,
            is_free=False,
            difficulty_level="advanced",
            programming_language="other",
            rating=4.9,
            is_featured=True
        )
        if not p5.thumbnail:
            p5.thumbnail.save("p5_thumb.jpg", dummy_thumb)
            p5.file.save("p5_file.zip", dummy_file)
            p5.save()

        p6, _ = Product.objects.get_or_create(
            title="MySQL Database Optimization Blueprint",
            slug="mysql-database-optimization-blueprint",
            category=system_cat,
            description="Optimize complex JOIN operations, write proper schema indexes, profile execution times, and set up replication logs in MySQL and PostgreSQL.",
            price=699.00,
            discount_price=399.00,
            is_free=False,
            difficulty_level="intermediate",
            programming_language="mysql",
            rating=4.6,
            is_featured=False
        )
        if not p6.thumbnail:
            p6.thumbnail.save("p6_thumb.jpg", dummy_thumb)
            p6.file.save("p6_file.zip", dummy_file)
            p6.save()

        # 4. Create Coupons
        Coupon.objects.get_or_create(code="WELCOME10", discount_percentage=10, is_active=True)
        Coupon.objects.get_or_create(code="BOBBY20", discount_percentage=20, is_active=True)
        Coupon.objects.get_or_create(code="PYTHON15", discount_percentage=15, is_active=True)

        # 5. Create Blog Posts
        b1, _ = Post.objects.get_or_create(
            title="5 Career Tips for Backend Django Developers in 2026",
            slug="django-career-tips-2026",
            category="career_advice",
            tags="career, django, python, backend",
            views=142,
            content_markdown="""# 5 Career Tips for Django Developers

As we navigate through 2026, backend roles are demanding more architectural expertise. Here are 5 tips to stand out:

1. **Master Django REST Framework & Ninja**: API design is crucial. Learn schema validations and performance caching.
2. **Build Async Architectures**: Familiarize yourself with Django's async views, ASGI, and websockets.
3. **Database Indexing**: Slow queries kill user experiences. Understand indexes, query profiling, and explain queries.
4. **Deploy on VPS and Dockerize**: Hosting apps requires containerization skill. Master docker-compose.
5. **Publish Code Repositories**: Show, don't tell! Open-source templates help prove skill sets.
"""
        )
        if not b1.thumbnail:
            b1.thumbnail.save("b1_thumb.jpg", dummy_thumb)
            b1.save()

        # 6. Create Services
        self.stdout.write("Seeding Services...")
        Service.objects.get_or_create(
            icon="fa-solid fa-code",
            title="Website Development",
            description="Complete responsive modern frontends built with clean HTML5/CSS3 and optimized for fast Google page speeds.",
            starting_price="₹15,000",
            order=1
        )
        Service.objects.get_or_create(
            icon="fa-brands fa-python",
            title="Django Development",
            description="Robust backend database schemas, REST APIs, custom admins, Celery asynchronous runners, and Stripe checkout integrations.",
            starting_price="₹25,000",
            order=2
        )
        Service.objects.get_or_create(
            icon="fa-solid fa-cart-shopping",
            title="Ecommerce Development",
            description="SaaS storefront templates with offline UPI validators, full shopping cart drawer pages, and digital files downloads.",
            starting_price="₹35,000",
            order=3
        )
        Service.objects.get_or_create(
            icon="fa-solid fa-palette",
            title="Landing Page Design",
            description="Conversion-optimized single-page layouts featuring custom visual assets, glassmorphic headers, and email capture hooks.",
            starting_price="₹9,999",
            order=4
        )
        Service.objects.get_or_create(
            icon="fa-solid fa-laptop-code",
            title="Portfolio Websites",
            description="Modern, responsive portfolios highlighting your projects, career steps, skills timeline, and contact alerts.",
            starting_price="₹12,000",
            order=5
        )

        # 7. Create Testimonials
        self.stdout.write("Seeding Testimonials...")
        Testimonial.objects.get_or_create(
            name="Elena Rostova",
            title="Founder, DesignSaaS",
            rating=5,
            feedback="Bobby built a custom landing page and payment flow for our design studio. He was extremely fast, responsive, and completed the work well ahead of our launch schedule. Our signup rates increased by 40%!",
            order=1
        )
        Testimonial.objects.get_or_create(
            name="Devon Vance",
            title="Technical Architect, FinSync",
            rating=5,
            feedback="The Django scalability blueprint ebook is an absolute masterpiece. Bobby's chapters on ORM prefetching and PostgreSQL transaction locking saved our team days of deployment troubleshooting.",
            order=2
        )
        Testimonial.objects.get_or_create(
            name="Karan Sharma",
            title="Software Engineer, TechCore",
            rating=5,
            feedback="Bobby's practice guides and coding notes helped me structure my Python code. I was able to pass three backend rounds and secure my dream role. Highly recommend Bobby's coaching!",
            order=3
        )

        # 8. Create Projects
        self.stdout.write("Seeding Projects...")
        p_proj1, _ = Project.objects.get_or_create(
            title="SnippetSaver CLI Tool",
            slug="snippetsaver-cli-tool",
            technologies="Python, SQLite, Rich CLI",
            short_description="A python CLI utility to help developers backup, highlight, search, and parse code snippets directly from their terminals.",
            description="""<h3>Project Walkthrough</h3><p>SnippetSaver solves snippet clutter. It is written in pure Python 3.10 and leverages SQLite3 for fast local caching. Rich CLI handles beautiful console formatting.</p>
<h4>System Requirements</h4>
<ul>
  <li>Python >= 3.8</li>
  <li>sqlite3 extension active</li>
</ul>
<pre><code class="language-python"># Run query
import sqlite3
conn = sqlite3.connect('snippets.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM snippets WHERE tag='django'")
</code></pre>""",
            live_url="https://github.com"
        )
        if not p_proj1.thumbnail:
            p_proj1.thumbnail.save("proj1_thumb.jpg", dummy_thumb)
            p_proj1.save()

        p_proj2, _ = Project.objects.get_or_create(
            title="Django E-commerce API Engine",
            slug="django-ecommerce-api-engine",
            technologies="Django, PostgreSQL, Redis, Celery",
            short_description="An enterprise-grade headless REST API providing complete checkout flows, coupon validation structures, and automated PDF invoice generation.",
            description="""<h3>System Architecture</h3><p>This API engine acts as the headless backend for large e-commerce platforms. Built with Django REST Framework, using Redis for session caching and Celery workers to handle billing queues.</p>
<pre><code class="language-python"># Celery Task for billing
@shared_task
def send_billing_invoice(order_id):
    order = Order.objects.get(id=order_id)
    pdf = generate_pdf_invoice(order)
    send_mail_with_attachment(order.user.email, pdf)
</code></pre>""",
            live_url="https://github.com"
        )
        if not p_proj2.thumbnail:
            p_proj2.thumbnail.save("proj2_thumb.jpg", dummy_thumb)
            p_proj2.save()

        # 9. Create Languages & Topics (Academy)
        self.stdout.write("Seeding Languages & Topics...")
        python_lang, _ = Language.objects.get_or_create(
            name="Python",
            slug="python",
            icon="fa-brands fa-python",
            description="Master Python fundamentals: variables, lists, functions, OOP, decorators, and memory optimization.",
            is_active=True
        )
        if not python_lang.thumbnail:
            python_lang.thumbnail.save("py_thumb.jpg", dummy_thumb)
            python_lang.save()

        django_lang, _ = Language.objects.get_or_create(
            name="Django",
            slug="django",
            icon="fa-solid fa-server",
            description="Build robust web applications: ORM, prefetching, custom middleware, templates, REST APIs, and deployment.",
            is_active=True
        )
        if not django_lang.thumbnail:
            django_lang.thumbnail.save("dj_thumb.jpg", dummy_thumb)
            django_lang.save()

        # Topics for Python
        Topic.objects.get_or_create(
            language=python_lang,
            title="Variables & Data Types",
            slug="python-variables-and-data-types",
            content="""<p>In Python, variables are dynamically typed. This means you do not need to declare their type explicitly before assignment.</p>
<h4>Code Example</h4>
<pre><code class="language-python"># Variable declarations
name = "BobbyTheCoder"
age = 26
skills = ["Python", "Django", "SQL"]
is_active = True

print(f"Developer {name} is {age} years old.")
</code></pre>
<div class="code-output-box">
Developer BobbyTheCoder is 26 years old.
</div>
<div class="learn-note-box">
  <h5>Memory Management Note</h5>
  <p>Python variables act as reference pointers to objects in memory. Assigning variables duplicates references, not the actual values themselves.</p>
</div>""",
            difficulty="beginner",
            order=1
        )

        Topic.objects.get_or_create(
            language=python_lang,
            title="List Comprehensions",
            slug="python-list-comprehensions",
            content="""<p>List comprehensions provide a concise way to create lists. They can replace standard for-loops and filter operations easily.</p>
<h4>Syntax Structure</h4>
<pre><code class="language-python"># Standard Loop
squares = []
for x in range(5):
    squares.append(x**2)

# List Comprehension
squares_comp = [x**2 for x in range(5)]
print(squares_comp)
</code></pre>
<div class="code-output-box">
[0, 1, 4, 9, 16]
</div>""",
            difficulty="beginner",
            order=2
        )

        # Topics for Django
        Topic.objects.get_or_create(
            language=django_lang,
            title="Understanding Django Middleware",
            slug="django-understanding-middleware",
            content="""<p>Middleware is a framework of hooks into Django's request/response processing. It is a light, low-level plugin system for globally altering Django's input or output.</p>
<h4>Custom Middleware Example</h4>
<pre><code class="language-python">class ExecutionTimeLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import time
        start = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start
        print(f"Request path {request.path} took {duration:.4f}s")
        return response
</code></pre>""",
            difficulty="intermediate",
            order=1
        )

        self.stdout.write("Database seeding complete!")
