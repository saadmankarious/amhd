import os
import json
import re
from collections import defaultdict

# Keywords to scan for in posts
keywords = [
    "تشخيص", "شُخِّصَ", "تم التشخيص", "تم تشخيصي", "طبيب نفسي", "الأخصائي النفسي",
    "صحة نفسية", "حالة نفسية", "Mental health", "Mental state", "اضطراب القلق",
    "قلق", "التوتر", "Anxiety disorder", "Anxiety", "Stress", "اضطراب الهلع",
    "Panic disorder", "الهلع", "Panic attacks", "الخوف المرضي", "رهاب", "Phobia",
    "رهاب اجتماعي", "Social anxiety", "اضطراب قلق عام", "Generalized anxiety disorder",
    "GAD", "اضطراب المزاج", "Mood disorder", "اكتئاب", "Depression", "الاكتئاب الحاد",
    "Major depressive disorder", "Clinical depression", "اضطراب اكتئابي", "Depressive disorder",
    "الحزن المزمن", "Persistent depressive disorder", "Dysthymia", "اضطراب ثنائي القطب",
    "Bipolar disorder", "اضطراب المزاج ثنائي القطب", "Manic-depressive illness", "الوسواس القهري",
    "Obsessive-Compulsive Disorder", "OCD", "اضطراب الوسواس القهري", "Obsessive disorder",
    "وسواس", "Obsessions", "الأفعال القهرية", "Compulsions", "اضطراب شد الشعر",
    "Trichotillomania", "نتف الشعر", "Hair-pulling disorder", "اضطراب قضم الأظافر",
    "Nail-biting disorder", "التوحد", "Autism", "اضطراب طيف التوحد", "Autism spectrum disorder",
    "ASD", "فرط الحركة", "Hyperactivity", "اضطراب فرط الحركة وتشتت الانتباه",
    "Attention Deficit Hyperactivity Disorder", "ADHD", "نقص الانتباه", "ADD",
    "Attention Deficit Disorder", "تأخر النمو العصبي", "Neurodevelopmental delay",
    "اضطراب ما بعد الصدمة", "Post-Traumatic Stress Disorder", "PTSD", "صدمة نفسية", "Trauma",
    "اضطراب الكرب التالي للصدمة", "الإجهاد المزمن", "Chronic stress", "اضطراب التكيف",
    "Adjustment disorder", "اضطراب الأكل", "Eating disorder", "فقدان الشهية العصبي",
    "Anorexia nervosa", "الشره المرضي العصبي", "Bulimia nervosa", "اضطراب نهم الطعام",
    "Binge-eating disorder", "اضطراب الطعام الانتقائي", "Selective eating disorder",
    "الفصام", "Schizophrenia", "انفصام الشخصية", "اضطراب ذهاني", "Psychotic disorder",
    "الذهان", "Psychosis", "الهلاوس", "Hallucinations", "اضطراب الوهم", "Delusional disorder",
    "اضطراب الشخصية", "Personality disorder", "اضطراب الشخصية الحدية", "Borderline personality disorder",
    "BPD", "اضطراب الشخصية النرجسية", "Narcissistic personality disorder", "NPD",
    "اضطراب الشخصية الانعزالية", "Avoidant personality disorder", "اضطراب الشخصية الانطوائية",
    "Introverted personality disorder", "أفكار انتحارية", "Suicidal thoughts", "ميل للانتحار",
    "Suicidal tendencies", "محاولات الانتحار", "Suicide attempts", "إيذاء النفس", "Self-harm",
    "جروح النفس", "Cutting", "Self-injury", "الأرق", "Insomnia", "اضطراب النوم", "Sleep disorder",
    "انقطاع النفس النومي", "Sleep apnea", "فرط النوم", "Hypersomnia", "اضطراب الهوية التفارقي",
    "Dissociative identity disorder", "DID", "اضطراب جنون الارتياب", "Paranoia", "القلق الاجتماعي",
    "Social anxiety", "اضطراب ضعف التركيز", "Concentration disorder", "الانعزال", "Isolation"
]

diagnosis_phrases = [
    "أنا مصاب بـ", "أعاني من", "تشخيصي هو", "تم تشخيصي بـ", "تشخيص الطبيب هو", "تم التأكيد على إصابتي بـ",
    "قال لي الطبيب أنني مصاب بـ", "أشعر بأعراض", "أعتقد أنني أعاني من", "قد أكون مصاب بـ",
    "لدي أعراض تشير إلى", "أظن أنني أعاني من", "أواجه مشاكل مرتبطة بـ", "قال لي الطبيب أنني أعاني من",
    "قالت لي العيادة أنني مصاب بـ", "تم تشخيص حالتي على أنها", "تقرير التشخيص يشير إلى", "تم إثبات إصابتي بـ",
    "أكد الطبيب إصابتي بـ", "تم تشخيصي مؤخرًا بـ", "نتائج الفحوصات تشير إلى", "قال لي الطبيب أنني أعاني من أعراض",
    "تشخيص المرض كان", "حالة الطبيب ذكرت أنني مصاب بـ", "التشخيص النهائي يشير إلى", "تم إعلامي من الطبيب أنني مصاب بـ",
    "التشخيص الذي حصلت عليه هو", "تم إعلامي رسميًا أنني أعاني من", "الأعراض التي أعاني منها تؤكد أنني مصاب بـ",
    "أشعر أنني أعاني من أعراض", "تشخيص حالتي يبين", "قد أكد لي الطبيب أنني أعاني من", "تشخيصي الطبي هو",
    "أنا عندي", "عندي", "أنا حاسس بأعراض", "حاسس إني عندي", "قال الدكتور عندك", "قال الدكتور إني عندي",
    "قالولي عندك", "قالولي إني عندي", "أنا متأكد إني عندي", "حاسس إن عندي مشكلة بـ", "حسيت إني عندي",
    "عندي مشكلة بـ", "قالولي التشخيص عندك هو", "عندي أعراض تشير إلى", "أنا عندي مشكلة في"
]

# Initialize statistics dictionary
stats = defaultdict(lambda: {"count": 0, "user_ids": []})

# Function to scan JSONL files for matching posts
def scan_jsonl_files_for_keywords(folder_path, char_range=40):
    for filename in os.listdir(folder_path):
        if filename.endswith('.jsonl'):  # Only process .jsonl files
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {filename}")
            with open(file_path, 'r', encoding='utf-8') as file:
                line_number = 0
                for line in file:
                    line_number += 1
                    try:
                        post = json.loads(line)  # Parse each line as JSON
                        check_post_for_proximity(post, filename, line_number, char_range)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON on line {line_number} in file {filename}")

# Function to check proximity of diagnosis phrases and keywords
def check_post_for_proximity(post, source_file, line_number, char_range):
    title = post.get('title', '')
    selftext = post.get('selftext', '')
    user_id = post.get('user_id', 'unknown')

    # Combine title and selftext for proximity search
    content = f"{title} {selftext}"

    for phrase in diagnosis_phrases:
        for keyword in keywords:
            # Find all occurrences of the diagnosis phrase
            phrase_matches = [(m.start(), m.end()) for m in re.finditer(re.escape(phrase), content)]
            # Find all occurrences of the keyword
            keyword_matches = [(m.start(), m.end()) for m in re.finditer(re.escape(keyword), content)]

            # Check proximity between phrase and keyword
            for phrase_start, phrase_end in phrase_matches:
                for keyword_start, keyword_end in keyword_matches:
                    if abs(phrase_start - keyword_start) <= char_range or abs(keyword_end - phrase_end) <= char_range:
                        # Update stats
                        stats[keyword]["count"] += 1
                        if user_id not in stats[keyword]["user_ids"]:
                            stats[keyword]["user_ids"].append(user_id)
                        return  # Stop further checks for this post once a match is found

# Specify the folder containing JSONL files
folder_path = "../arctic"  # Replace with your folder path

# Scan the folder for matching posts with a proximity range of 40 characters
scan_jsonl_files_for_keywords(folder_path, char_range=40)

# Save stats to a JSON file
output_file = "matching_stats.json"
with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(stats, json_file, ensure_ascii=False, indent=4)

print(f"Matching statistics saved to {output_file}")
