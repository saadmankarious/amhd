import os
import json
import sys

# List of Arabic keywords related to diagnosis and mental health
keywords = [
    # General Mental Health Terms
    "تشخيص", "شُخِّصَ", "تم التشخيص", "تم تشخيصي", "طبيب نفسي", "الأخصائي النفسي",
    "صحة نفسية", "حالة نفسية", "Mental health", "Mental state",
    
    # Anxiety Disorders
    "اضطراب القلق", "قلق", "التوتر", "Anxiety disorder", "Anxiety", "Stress",
    "اضطراب الهلع", "Panic disorder", "الهلع", "Panic attacks", "الخوف المرضي",
    "رهاب", "Phobia", "رهاب اجتماعي", "Social anxiety", "اضطراب قلق عام",
    "Generalized anxiety disorder", "GAD",
    
    # Mood Disorders
    "اضطراب المزاج", "Mood disorder", "اكتئاب", "Depression", "الاكتئاب الحاد",
    "Major depressive disorder", "Clinical depression", "اضطراب اكتئابي",
    "Depressive disorder", "الحزن المزمن", "Persistent depressive disorder",
    "Dysthymia", "اضطراب ثنائي القطب", "Bipolar disorder", "اضطراب المزاج ثنائي القطب",
    "Manic-depressive illness",
    
    # Obsessive-Compulsive and Related Disorders
    "الوسواس القهري", "Obsessive-Compulsive Disorder", "OCD", "اضطراب الوسواس القهري",
    "Obsessive disorder", "وسواس", "Obsessions", "الأفعال القهرية", "Compulsions",
    "اضطراب شد الشعر", "Trichotillomania", "نتف الشعر", "Hair-pulling disorder",
    "اضطراب قضم الأظافر", "Nail-biting disorder",
    
    # Neurodevelopmental Disorders
    "التوحد", "Autism", "اضطراب طيف التوحد", "Autism spectrum disorder", "ASD",
    "فرط الحركة", "Hyperactivity", "اضطراب فرط الحركة وتشتت الانتباه",
    "Attention Deficit Hyperactivity Disorder", "ADHD", "نقص الانتباه",
    "ADD", "Attention Deficit Disorder", "تأخر النمو العصبي", "Neurodevelopmental delay",
    
    # Trauma and Stress-Related Disorders
    "اضطراب ما بعد الصدمة", "Post-Traumatic Stress Disorder", "PTSD", "صدمة نفسية",
    "Trauma", "اضطراب الكرب التالي للصدمة", "الإجهاد المزمن", "Chronic stress",
    "اضطراب التكيف", "Adjustment disorder",
    
    # Eating Disorders
    "اضطراب الأكل", "Eating disorder", "فقدان الشهية العصبي", "Anorexia nervosa",
    "الشره المرضي العصبي", "Bulimia nervosa", "اضطراب نهم الطعام", "Binge-eating disorder",
    "اضطراب الطعام الانتقائي", "Selective eating disorder",
    
    # Psychotic Disorders
    "الفصام", "Schizophrenia", "انفصام الشخصية", "اضطراب ذهاني", "Psychotic disorder",
    "الذهان", "Psychosis", "الهلاوس", "Hallucinations", "اضطراب الوهم", "Delusional disorder",
    
    # Personality Disorders
    "اضطراب الشخصية", "Personality disorder", "اضطراب الشخصية الحدية",
    "Borderline personality disorder", "BPD", "اضطراب الشخصية النرجسية",
    "Narcissistic personality disorder", "NPD", "اضطراب الشخصية الانعزالية",
    "Avoidant personality disorder", "اضطراب الشخصية الانطوائية", "Introverted personality disorder",
    
    # Suicidal Thoughts and Self-Harm
    "أفكار انتحارية", "Suicidal thoughts", "ميل للانتحار", "Suicidal tendencies",
    "محاولات الانتحار", "Suicide attempts", "إيذاء النفس", "Self-harm", "جروح النفس",
    "Cutting", "Self-injury",
    
    # Sleep Disorders
    "الأرق", "Insomnia", "اضطراب النوم", "Sleep disorder", "انقطاع النفس النومي",
    "Sleep apnea", "فرط النوم", "Hypersomnia",
    
    # Other Common Disorders
    "اضطراب الهوية التفارقي", "Dissociative identity disorder", "DID",
    "اضطراب جنون الارتياب", "Paranoia", "القلق الاجتماعي", "Social anxiety",
    "اضطراب ضعف التركيز", "Concentration disorder", "الانعزال", "Isolation"
]

# Function to scan a single file and extract relevant posts
def scan_file_for_keywords(file_path):
    relevant_posts = []

    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            data = json.load(file)
            if isinstance(data, list):  # Assuming the file might contain a list of messages
                for entry in data:
                    message = entry.get("message", "")
                    if any(keyword in message for keyword in keywords):
                        relevant_posts.append(entry)
            else:
                message = data.get("message", "")
                if any(keyword in message for keyword in keywords):
                    relevant_posts.append(data)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {file_path}")
    
    return relevant_posts

# Main execution
if len(sys.argv) < 2:
    print("Usage: python script.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]
if not os.path.isfile(file_path):
    print(f"File not found: {file_path}")
    sys.exit(1)

# Scan the file and print relevant posts
relevant_posts = scan_file_for_keywords(file_path)
print(f"Found {len(relevant_posts)} posts")

for post in relevant_posts:
    print(f"Date: {post.get('date', 'N/A')}, Sender: {post.get('sender', 'N/A')}, Message: {post.get('message', 'N/A')}\n")
