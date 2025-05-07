import re
import PyPDF2
import phonenumbers
from typing import Dict, List, Any, Optional
import io
import regex
from email_validator import validate_email, EmailNotValidError

from app.models.resume_model import Resume, Education, Experience, Project


class PDFExtractor:
    def __init__(self):
        # Common patterns to search for
        self.patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'(\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            "linkedin": r'linkedin\.com/in/[\w-]+',
            "github": r'github\.com/[\w-]+',
            "education_keywords": ["education", "academic", "university", "college", "degree", "bachelor", "master", "phd"],
            "experience_keywords": ["experience", "employment", "work", "job", "professional"],
            "skills_keywords": ["skills", "technical skills", "technologies", "competencies", "proficiencies"],
            "projects_keywords": ["projects", "technical projects", "academic projects", "personal projects"],
            "achievements_keywords": ["achievements", "awards", "honors", "recognition", "certifications", "accomplishments"],
        }
        self.common_skills = [
            "java", "python", "c++", "javascript", "typescript", "c#", "ruby", "go", "php", "swift", "kotlin", 
            "sql", "nosql", "mongodb", "postgresql", "mysql", "oracle", "redis", "firebase", "graphql", 
            "html", "css", "sass", "less", "react", "angular", "vue", "node", "express", "spring", "django",
            "flask", "laravel", "asp.net", "jquery", "bootstrap", "tailwind", "redux", "graphql", "rest", "soap",
            "git", "github", "gitlab", "bitbucket", "docker", "kubernetes", "jenkins", "ci/cd", "aws", "azure", 
            "gcp", "agile", "scrum", "jira", "confluence", "kanban", "tdd", "unit testing", "integration testing",
            "data structures", "algorithms", "oop", "functional programming", "microservices", "mvc", "mvvm",
            "design patterns", "authentication", "authorization", "security", "jwt", "oauth", "multithreading",
            "concurrency", "asynchronous", "reactive", "event-driven", "serverless", "machine learning", "ai",
            "data analysis", "big data", "hadoop", "spark", "kafka", "etl", "data visualization", "tableau", 
            "power bi", "database design", "orm", "jpa", "hibernate", "entity framework", "webpack",
            "babel", "eslint", "prettier", "linux", "unix", "windows", "macos", "bash", "powershell",
            "restful api", "websockets", "json", "xml", "yaml", "postman", "swagger", "api gateway",
            "load balancing", "caching", "cdn", "seo", "accessibility", "responsive design", "mobile development",
            "android", "ios", "flutter", "react native", "xamarin", "cordova", "object-oriented", "solid principles",
            "apache", "nginx", "iis", "agile methodologies", "code review", "clean code", "refactoring",
            "performance optimization", "memory management", "networking", "http", "https", "tcp/ip"
        ]
        
        # Common interview topics based on technical skills
        self.interview_topics = [
            "Data Structures and Algorithms", "Object-Oriented Programming", 
            "Database Management System", "RESTful API Design", 
            "Authentication & Authorization", "Multithreading",
            "Java Programming", "Python Programming", "C++ Programming", 
            "Spring Boot", "Design Patterns", "Microservices Architecture",
            "System Design", "SQL and Database Design", "ORM Frameworks",
            "Unit Testing", "CI/CD Pipelines", "Software Development Lifecycle",
            "Web Development", "Frontend Frameworks", "Backend Development"
        ]


    def extract_from_pdf(self, file_content: bytes) -> Resume:
        file_obj = io.BytesIO(file_content)
        reader = PyPDF2.PdfReader(file_obj)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        data = self._process_text(text)
        return Resume(**data)
    

    def _process_text(self, text: str) -> Dict[str, Any]:
        """Process extracted text and structure into resume sections"""
        resume_data = {
            "name": "Not Present",
            "email": "Not Present",
            "phone": "Not Present", 
            "linkedin": "Not Present",
            "github": "Not Present",
            "skills": [],
            "education": [],
            "experience": [],
            "projects": [],
            "achievements": [],
            "interview_topics": []
        }
        
        # Extract name (usually at the beginning of the resume)
        # Look for name in first few lines
        lines = text.splitlines()
        for i, line in enumerate(lines[:5]):  # Check first 5 lines for name
            line = line.strip()
            if line and len(line) < 40:  # Names are typically short
                # Pattern for first and last name with possible middle name/initial
                if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+$', line):
                    resume_data["name"] = line
                    break
                # Pattern for ALL CAPS name
                elif re.match(r'^[A-Z]{2,}(?:\s+[A-Z]{2,})+$', line):
                    resume_data["name"] = line.title()  # Convert to title case
                    break
                # Fallback for other name formats
                elif re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', line):
                    resume_data["name"] = line
                    break
        
        # Extract email
        email_match = re.search(self.patterns["email"], text)
        if email_match:
            email = email_match.group()
            try:
                # Validate email
                validate_email(email)
                resume_data["email"] = email
            except EmailNotValidError:
                pass
        
        # Extract phone
        phone_match = re.search(self.patterns["phone"], text)
        if phone_match:
            phone = phone_match.group()
            # Clean up phone number
            phone = re.sub(r'[^0-9+]', '', phone)  # Remove non-digit and non-plus characters
            if len(phone) >= 10:  # Ensure we have at least 10 digits
                resume_data["phone"] = phone
        
        # Extract LinkedIn
        linkedin_match = re.search(self.patterns["linkedin"], text)
        if linkedin_match:
            resume_data["linkedin"] = linkedin_match.group()
        
        # Extract GitHub
        github_match = re.search(self.patterns["github"], text)
        if github_match:
            resume_data["github"] = github_match.group()
        
        # Split text into sections
        sections = self._split_into_sections(text)
        
        # Extract education
        education_section = self._find_section(sections, self.patterns["education_keywords"])
        if education_section:
            resume_data["education"] = self._extract_education(education_section)
        
        # Extract experience
        experience_section = self._find_section(sections, self.patterns["experience_keywords"])
        if experience_section:
            resume_data["experience"] = self._extract_experience(experience_section)
        
        # Extract skills
        skills_section = self._find_section(sections, self.patterns["skills_keywords"])
        if skills_section:
            resume_data["skills"] = self._extract_skills(skills_section)
        else:
            # Try to extract skills from the entire text if no dedicated section
            resume_data["skills"] = self._extract_skills(text)
        
        # Extract projects
        projects_section = self._find_section(sections, self.patterns["projects_keywords"])
        if projects_section:
            resume_data["projects"] = self._extract_projects(projects_section)
        
        # Extract achievements
        achievements_section = self._find_section(sections, self.patterns["achievements_keywords"])
        if achievements_section:
            resume_data["achievements"] = self._extract_achievements(achievements_section)
        
        # Generate interview topics based on skills
        resume_data["interview_topics"] = self._generate_interview_topics(resume_data["skills"])
        
        return resume_data
    
    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Split resume text into different sections based on headers"""
        sections = {}
        
        # Common section headers in resumes
        section_headers = [
            "education", "experience", "work experience", "professional experience",
            "skills", "technical skills", "projects", "technical projects",
            "achievements", "awards", "honors", "certifications", "accomplishments",
            "summary", "objective", "profile", "about", "interests", "activities",
            "publications", "volunteer", "extracurricular"
        ]
        
        # Create regex pattern for section headers
        pattern = r'(?i)(?:^|\n)(?:[ \t]*)((?:' + '|'.join(section_headers) + r')(?:\s*:|\s*$))'
        
        # Find potential section headers
        matches = list(re.finditer(pattern, text, re.MULTILINE))
        
        if not matches:
            # Try a more lenient pattern if no headers found
            pattern = r'(?i)(?:^|\n)(?:[ \t]*)((?:' + '|'.join(section_headers) + r')(?:\s*))(?=\n)'
            matches = list(re.finditer(pattern, text, re.MULTILINE))
        
        # Split text by the found headers
        for i in range(len(matches)):
            start_idx = matches[i].start()
            end_idx = matches[i+1].start() if i < len(matches) - 1 else len(text)
            section_name = matches[i].group(1).strip().lower().rstrip(':')
            section_content = text[start_idx:end_idx].strip()
            sections[section_name] = section_content
        
        # Handle case where no sections were found
        if not sections:
            sections["full_text"] = text
        
        return sections
    
    def _find_section(self, sections: Dict[str, str], keywords: List[str]) -> Optional[str]:
        """Find a section based on keywords"""
        for section_name, content in sections.items():
            for keyword in keywords:
                if keyword.lower() in section_name.lower():
                    return content
        return None
    
    def _extract_education(self, text: str) -> List[Education]:
        """Extract education details"""
        education_list = []
        
        # Look for patterns like "University/College Name", "Degree Program", "CGPA/GPA", "Year-Year"
        education_entries = re.split(r'\n\s*\n', text)
        
        for entry in education_entries:
            if len(entry.strip()) == 0:
                continue
                
            edu = Education()
            
            # Extract institution - remove "Education/" prefix if it exists
            institution_match = re.search(r'([A-Z][A-Za-z\s,&]+(?:University|College|Institute|School|Academy))', entry)
            if institution_match:
                institution = institution_match.group(1).strip()
                # Remove "Education/" prefix if it exists
                institution = re.sub(r'^Education/\s*', '', institution)
                edu.institution = institution
            
            # Extract location
            location_match = re.search(r'([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)?)', entry)
            if location_match and not any(keyword in location_match.group(1) for keyword in ["University", "College", "Institute", "School", "Academy"]):
                edu.location = location_match.group(1).strip()
            
            # Extract degree
            degree_match = re.search(r'(Bachelor|Master|PhD|B\.Tech|M\.Tech|B\.E\.|M\.E\.|B\.S\.|M\.S\.|B\.A\.|M\.A\.)(?:\s+of\s+|\s+in\s+)?\s*([A-Za-z\s&]+)', entry, re.IGNORECASE)
            if degree_match:
                prefix = degree_match.group(1)
                field = degree_match.group(2) if degree_match.group(2) else ""
                edu.degree = f"{prefix} of {field}".strip() if field else prefix
            
            # Extract CGPA/GPA
            cgpa_match = re.search(r'(?:CGPA|GPA)(?:\s*[:=]\s*|\s+)(\d+\.\d+)(?:/(\d+))?', entry, re.IGNORECASE)
            if cgpa_match:
                cgpa = cgpa_match.group(1)
                scale = cgpa_match.group(2) if cgpa_match.group(2) else "10"  # Default scale
                edu.cgpa = f"{cgpa}/{scale}"
            
            # Extract time period
            period_match = re.search(r'(\d{4})(?:\s*[-–]\s*|\s+to\s+)(\d{4}|Present)', entry)
            if period_match:
                start = period_match.group(1)
                end = period_match.group(2)
                edu.period = f"{start}-{end}"
            
            if edu.institution != "Not Present" or edu.degree != "Not Present":
                education_list.append(edu)
        
        return education_list
    
    def _extract_experience(self, text: str) -> List[Experience]:
        """Extract work experience"""
        experience_list = []
        
        # Split by empty lines to get different experience entries
        experience_entries = re.split(r'\n\s*\n', text)
        
        for entry in experience_entries:
            if len(entry.strip()) == 0:
                continue
                
            exp = Experience()
            
            # Extract company name - look for names that are likely companies
            company_match = re.search(r'([A-Z][A-Za-z0-9\s&,.]+(?:Inc|LLC|Ltd|Corp|Corporation|Company|Technologies|Solutions|Systems|Group|Associates))', entry)
            if company_match:
                exp.company = company_match.group(1).strip()
            else:
                # Fallback: look for words in all caps or title case at the beginning of entry
                company_match = re.search(r'^([A-Z][A-Za-z0-9\s&,.]+)', entry)
                if company_match:
                    exp.company = company_match.group(1).strip()
            
            # Extract position
            position_match = re.search(r'((?:Senior|Junior|Lead|Principal|Chief|Associate|Assistant|Staff|Technical|Software|Full Stack|Backend|Frontend|DevOps|Data|Cloud|Security|Network|Mobile|Web|UI/UX|QA|Test)(?:\s+[A-Za-z]+)*(?:\s+(?:Developer|Engineer|Architect|Manager|Director|Specialist|Analyst|Consultant|Intern|Administrator|Programmer|Designer|Scientist|Researcher)))', entry, re.IGNORECASE)
            if position_match:
                exp.position = position_match.group(1).strip()
            
            # Extract location
            location_match = re.search(r'([A-Z][a-z]+(?:,\s*[A-Z][a-z]+)?)', entry)
            if location_match and exp.company != location_match.group(1):
                exp.location = location_match.group(1).strip()
            
            # Extract period - improved pattern to capture various date formats
            period_match = re.search(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:uary|ruary|ch|il|e|y|ust|tember|ober|ember)?(?:\s+\d{4})|(?:\d{2}|\d{4}))(?:\s*(?:–|-|to|—|through)\s*)((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:uary|ruary|ch|il|e|y|ust|tember|ober|ember)?(?:\s+\d{4})|(?:\d{2}|\d{4})|Present|Current)', entry, re.IGNORECASE)
            if period_match:
                exp.period = f"{period_match.group(1)} - {period_match.group(2)}"
            
            # Extract responsibilities (often bullet points)
            responsibilities = []
            bullet_points = re.findall(r'(?:^|\n)(?:\s*[•∙■◦◘○◙*-]\s*|\s*\d+\.\s*|\s*[▪▫]\s*)(.+?)(?=\n(?:\s*[•∙■◦◘○◙*-]\s*|\s*\d+\.\s*|\s*[▪▫]\s*)|$)', entry)
            if bullet_points:
                responsibilities = [point.strip() for point in bullet_points if point.strip()]
            
            # If no bullet points found, try to extract sentences that might be responsibilities
            if not responsibilities:
                sentences = re.findall(r'(?:^|\n)\s*([A-Z][\w\s,;:\'".()-]+?\.)\s*(?=\n|$)', entry)
                if sentences:
                    responsibilities = [sentence.strip() for sentence in sentences if sentence.strip()]
            
            exp.responsibilities = responsibilities
            
            if exp.company != "Not Present" or exp.position != "Not Present":
                experience_list.append(exp)
        
        return experience_list
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        skills = []
        
        # Look for common skills in the text
        for skill in self.common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text.lower()):
                # Capitalize skill name properly
                formatted_skill = ' '.join(word.capitalize() if word.lower() != 'and' else word.lower() 
                                 for word in skill.split())
                skills.append(formatted_skill)
        
        # If skills were found using the common skills list
        if skills:
            return skills
        
        # Fallback: try to extract comma/bullet separated lists
        skill_lists = re.findall(r'(?:skills|technologies)(?::|include|are)?\s*(.+?)(?=\n\n|\n[A-Z]|$)', text, re.IGNORECASE)
        for skill_list in skill_lists:
            # Split by commas or bullet points
            individual_skills = re.split(r',|\s*[•∙■◦◘○◙*-]\s*', skill_list)
            for skill in individual_skills:
                skill = skill.strip()
                if skill and len(skill) > 1:  # Avoid single characters
                    skills.append(skill)
        
        return skills
    
    def _extract_projects(self, text: str) -> List[Project]:
        """Extract projects information"""
        projects_list = []
        
        # Split by empty lines or project headers to get different project entries
        project_entries = re.split(r'\n\s*\n', text)
        
        for entry in project_entries:
            if len(entry.strip()) == 0:
                continue
                
            project = Project()
            
            # Extract project name - look for a title at the beginning of the entry
            name_match = re.search(r'^([A-Z][A-Za-z0-9\s&\-:]+)', entry.strip())
            if name_match:
                project.name = name_match.group(1).strip()
            else:
                # Fallback: look for capitalized words that might be a project name
                name_match = re.search(r'([A-Z][A-Za-z0-9\s&\-:]+)(?:\||–|-|\n)', entry)
                if name_match:
                    project.name = name_match.group(1).strip()
            
            # Extract technologies
            tech_match = re.search(r'(?:Technologies|Tech Stack|Built with|Tools Used|Stack)(?::|\s*–\s*|\s*-\s*)?\s*(.+?)(?=\n|$)', entry, re.IGNORECASE)
            if tech_match:
                tech_list = re.split(r',|\s*[•∙■◦◘○◙*-]\s*', tech_match.group(1))
                project.technologies = [tech.strip() for tech in tech_list if tech.strip()]
            else:
                # Try to find technologies enclosed in brackets
                bracket_tech = re.search(r'\[(.*?)\]|\((.*?)\)', entry)
                if bracket_tech:
                    tech_group = bracket_tech.group(1) if bracket_tech.group(1) else bracket_tech.group(2)
                    tech_list = re.split(r',|\s*[•∙■◦◘○◙*-]\s*', tech_group)
                    project.technologies = [tech.strip() for tech in tech_list if tech.strip()]
            
            # Extract date
            date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(?:uary|ruary|ch|il|e|y|ust|tember|ober|ember)?\s+\d{4}', entry, re.IGNORECASE)
            if date_match:
                project.date = date_match.group(0)
            else:
                # Try just the year
                year_match = re.search(r'\b(20\d{2})\b', entry)
                if year_match:
                    project.date = year_match.group(1)
            
            # Extract descriptions (bullet points or lines that follow the project name)
            descriptions = []
            bullet_points = re.findall(r'(?:^|\n)(?:\s*[•∙■◦◘○◙*-]\s*|\s*\d+\.\s*|\s*[▪▫]\s*)(.+?)(?=\n(?:\s*[•∙■◦◘○◙*-]\s*|\s*\d+\.\s*|\s*[▪▫]\s*)|$)', entry)
            if bullet_points:
                descriptions = [point.strip() for point in bullet_points if point.strip()]
            
            # If no bullet points found, try to extract sentences that might be descriptions
            if not descriptions:
                # Skip the first line if it contains the project name
                lines = entry.strip().split('\n')
                if len(lines) > 1:
                    desc_text = '\n'.join(lines[1:])
                    sentences = re.findall(r'([A-Z][\w\s,;:\'".()-]+?\.)\s*(?=\n|$)', desc_text)
                    if sentences:
                        descriptions = [sentence.strip() for sentence in sentences if sentence.strip()]
            
            project.description = descriptions
            
            if project.name != "Not Present" or project.technologies:
                projects_list.append(project)
        
        return projects_list
    
    def _extract_achievements(self, text: str) -> List[str]:
        """Extract achievements"""
        achievements = []
        
        # Look for bullet points, numbered items or special characters
        bullet_points = re.findall(r'(?:^|\n)(?:\s*[•∙■◦◘○◙*-]\s*|\s*\d+[.)]\s*|\s*[▪▫]\s*)(.+?)(?=\n(?:\s*[•∙■◦◘○◙*-]\s*|\s*\d+[.)]\s*|\s*[▪▫]\s*)|$)', text)
        if bullet_points:
            achievements = [point.strip() for point in bullet_points if point.strip()]
        
        # If no bullet points found, try to extract sentences
        if not achievements:
            # Skip the first line if it's the section header
            lines = text.strip().split('\n')
            if len(lines) > 1 and any(keyword in lines[0].lower() for keyword in self.patterns["achievements_keywords"]):
                desc_text = '\n'.join(lines[1:])
                sentences = re.findall(r'([A-Z][\w\s,;:\'".()-]+?\.)\s*(?=\n|$)', desc_text)
                if sentences:
                    achievements = [sentence.strip() for sentence in sentences if sentence.strip()]
            else:
                sentences = re.findall(r'([A-Z][\w\s,;:\'".()-]+?\.)\s*(?=\n|$)', text)
                if sentences:
                    achievements = [sentence.strip() for sentence in sentences if sentence.strip()]
        
        # If still no achievements found, try to extract any non-empty lines
        if not achievements:
            lines = text.strip().split('\n')
            if len(lines) > 1:  # Skip the header
                achievements = [line.strip() for line in lines[1:] if line.strip()]
        
        return achievements
    
    def _generate_interview_topics(self, skills: List[str]) -> List[str]:
        """Generate potential interview topics based on skills"""
        topics = []
        
        # Add core topics that are always relevant
        core_topics = ["Data Structures and Algorithms", "Object-Oriented Programming", "Problem Solving"]
        topics.extend(core_topics)
        
        # Map skills to interview topics
        skill_to_topic = {
            "Java": ["Java Programming", "Spring Framework", "JVM Architecture"],
            "Python": ["Python Programming", "Flask/Django Frameworks", "Python Libraries"],
            "C++": ["C++ Programming", "Memory Management", "STL"],
            "SQL": ["Database Management System", "SQL Optimization", "Database Design"],
            "JavaScript": ["JavaScript", "Frontend Frameworks", "DOM Manipulation"],
            "React": ["React.js", "State Management", "Component Lifecycle"],
            "Angular": ["Angular", "TypeScript", "RxJS"],
            "Node.js": ["Node.js", "Express.js", "Server-side JavaScript"],
            "Spring Boot": ["Spring Boot", "Spring Security", "Spring Data"],
            "Hibernate": ["ORM Frameworks", "Hibernate", "JPA"],
            "Docker": ["Containerization", "Docker", "Kubernetes"],
            "AWS": ["Cloud Computing", "AWS Services", "Cloud Architecture"],
            "Git": ["Version Control", "Git", "CI/CD"],
            "Microservices": ["Microservices Architecture", "API Gateway", "Service Discovery"],
            "REST": ["RESTful API Design", "API Development", "HTTP Protocol"],
            "Authentication": ["Authentication & Authorization", "OAuth", "JWT"],
            "Multithreading": ["Multithreading", "Concurrency", "Parallel Processing"]
        }
        
        # Add topics based on identified skills
        for skill in skills:
            skill_lower = skill.lower()
            for key, related_topics in skill_to_topic.items():
                if key.lower() in skill_lower:
                    for topic in related_topics:
                        if topic not in topics:
                            topics.append(topic)
        
        # Ensure we don't have too many topics (limit to ~10)
        if len(topics) > 10:
            topics = topics[:10]
        
        return topics