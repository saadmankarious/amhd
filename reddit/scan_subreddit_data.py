import os
import json
import re
from collections import defaultdict
from tqdm import tqdm  # For live progress updates

keywords = [
    # Anxiety Disorders
    "اضطراب القلق", "القلق", "قلق", "التوتر", "توتر", "Anxiety disorder", "Anxiety", "Stress", 
    "اضطراب الهلع", "الهلع", "هلع", "Panic disorder", "Panic attacks", "الخوف المرضي", "خوف مرضي", 
    "رهاب", "Phobia", "رهاب اجتماعي", "Social anxiety", "اضطراب قلق عام", "Generalized anxiety disorder", 
    "GAD",

    # Mood Disorders
    "اضطراب المزاج", "المزاج", "مزاج", "Mood disorder", "اكتئاب", "اكتأب", "Depression", 
    "الاكتئاب الحاد", "اكتئاب حاد", "Major depressive disorder", "Clinical depression", 
    "اضطراب اكتئابي", "اكتئابي", "Depressive disorder", "الحزن المزمن", "حزن مزمن", 
    "Persistent depressive disorder", "Dysthymia", "اضطراب ثنائي القطب", "ثنائي القطب", 
    "Bipolar disorder", "Manic-depressive illness",

    # Obsessive-Compulsive and Related Disorders
    "الوسواس القهري", "وسواس قهري", "وسواس", "Obsessive-Compulsive Disorder", "OCD", 
    "اضطراب الوسواس القهري", "Obsessive disorder", "الأفعال القهرية", "أفعال قهرية", "Compulsions", 
    "اضطراب شد الشعر", "شد الشعر", "Trichotillomania", "نتف الشعر", "Hair-pulling disorder", 
    "اضطراب قضم الأظافر", "قضم الأظافر", "Nail-biting disorder",

    # Neurodevelopmental Disorders
    "التوحد", "توحد", "Autism", "اضطراب طيف التوحد", "طيف التوحد", "Autism spectrum disorder", 
    "ASD", "فرط الحركة", "فرط حركة", "Hyperactivity", "اضطراب فرط الحركة وتشتت الانتباه", 
    "فرط الحركة وتشتت الانتباه", "Attention Deficit Hyperactivity Disorder", "ADHD", "ADD", 
    "نقص الانتباه", "نقص انتباه", "Attention Deficit Disorder",

    # Eating Disorders
    "اضطراب الأكل", "اضطراب أكل", "Eating disorder", "فقدان الشهية العصبي", "فقدان الشهية", 
    "Anorexia nervosa", "الشره المرضي العصبي", "شره مرضي عصبي", "Bulimia nervosa", 
    "اضطراب نهم الطعام", "نهم الطعام", "Binge-eating disorder", "اضطراب الطعام الانتقائي", 
    "طعام انتقائي", "Selective eating disorder",

    # Psychotic Disorders
    "الفصام", "فصام", "Schizophrenia", "انفصام الشخصية", "فصام الشخصية", "اضطراب ذهاني", 
    "ذهاني", "Psychotic disorder", "الذهان", "ذهان", "Psychosis", "الهلاوس", "هلاوس", 
    "Hallucinations", "اضطراب الوهم", "وهم", "Delusional disorder",

    # Personality Disorders
    "اضطراب الشخصية", "الشخصية", "شخصية", "Personality disorder", "اضطراب الشخصية الحدية", 
    "الشخصية الحدية", "Personality disorder", "BPD", "اضطراب الشخصية النرجسية", 
    "الشخصية النرجسية", "Narcissistic personality disorder", "NPD", 
    "اضطراب الشخصية الانعزالية", "الشخصية الانعزالية", "Avoidant personality disorder", 
    "اضطراب الشخصية الانطوائية", "الشخصية الانطوائية", "Introverted personality disorder",

    # Suicidal Thoughts and Self-Harm
    "أفكار انتحارية", "فكر انتحاري", "Suicidal thoughts", "ميل للانتحار", "انتحار", 
    "Suicidal tendencies", "محاولات الانتحار", "محاولة انتحار", "Suicide attempts", 
    "إيذاء النفس", "إيذاء", "Self-harm", "جروح النفس", "جرح النفس", "Cutting", 
    "Self-injury",

    # Sleep Disorders
    "الأرق", "أرق", "Insomnia", "اضطراب النوم", "نوم مضطرب", "Sleep disorder", 
    "انقطاع النفس النومي", "نفس نومي", "فرط النوم", "فرط نوم", "Hypersomnia",

    # Dissociative Disorders
    "اضطراب الهوية التفارقي", "هوية تفارقية", "Dissociative identity disorder", "DID",

    # Paranoia and Related Disorders
    "اضطراب جنون الارتياب", "جنون الارتياب", "جنون ارتياب", "Paranoia",

    # Concentration Disorders
    "اضطراب ضعف التركيز", "ضعف التركيز", "Concentration disorder"
]

diagnosis_phrases = [
    # Standard Arabic Phrases
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
    "عندي مشكلة بـ", "قالولي التشخيص عندك هو", "عندي أعراض تشير إلى", "أنا عندي مشكلة في",

    # Egyptian Dialect Variations
    "أنا عندي", "عندي", "أنا كنت عند الدكتور وشخصني بـ", "الدكتور قالي عندك", "الدكتور قالي إني عندي",
    "تم تشخيصي عند الدكتور بـ", "قالولي عندك", "قالولي إني عندي", "شخصني الدكتور بـ", "شخصني الدكتور وقالي",
    "قالتلي الدكتورة عندك", "قالتلي الدكتورة إني عندي", "لقيت نفسي عندي", "طلعت عندي", "عرفت إني عندي",
    "عرفت إن أنا مصاب بـ", "أنا فعلاً عندي", "طلع تشخيصي هو", "تشخيص الدكتور كان", "طلع الدكتور قالي عندي",
    "الدكتور قاللي شخصي هو", "الدكتور أكد التشخيص بـ", "طلع تشخيصي عند الدكتور", "أنا بواجه مشكلة اسمها",
    "بعد التشخيص طلع عندي", "اتشخصت بـ", "طلع إن التشخيص هو", "اتأكدت من التشخيص بعد الدكتور",
    "شخصني الدكتور من فترة بـ", "آخر تشخيص قالي الدكتور هو", "اتشخصت من فترة بـ", "الدكتور أكد إصابتي بـ",
    "التحليل أثبت إن أنا عندي", "لقيت التحليل بيقول عندي", "شخصوني بـ", "طلع إن أنا عندي",

    # Variants with Dialectical Pronunciations
    "أنا شخصوني بـ", "شخصني الدكتور", "شخصت عند الدكتور بـ", "شخصوني مؤخراً بـ", "أنا فعلاً شخصوني بـ",
    "أنا اكتشفت إن عندي", "كنت مصاب بـ", "طلعت مصاب بـ", "التشخيص طلع كالتالي", "تشخيص الحالة كان",
    "أنا عندي مشكلة اسمها", "لقيت نفسي مصاب بـ", "اتضح إن التشخيص كان", "طلعت فعلاً عندي",
    "الدكتور شخصني من كام يوم بـ", "الدكتور شخصني النهاردة بـ", "تشخيصي النهائي هو", "لقيت الدكتور بيأكد عندي",
    "الدكتورة قالتلي عندك", "الدكتورة شخصتني بـ", "اتأكدت النهاردة إن عندي", "الدكتور أثبت التشخيص بـ",
    "أنا دلوقتي عرفت إني عندي", "اتشخصت النهاردة بـ", "شخصوني من يومين بـ", "شخصوني الأسبوع اللي فات بـ",

    # Formal/Medical Arabic Variations
    "تشخيص حالتي يشير إلى", "تشخيص الطبيب يوضح أنني أعاني من", "تشخيص الطبيب يؤكد أنني مصاب بـ",
    "تقرير الفحوصات أظهر أنني أعاني من", "نتائج الفحوصات أظهرت أنني مصاب بـ", "تقرير الفحوصات يوضح أنني مصاب بـ",
    "تشخيصي الطبي الحالي هو", "تشخيصي الطبي الأخير يوضح أنني مصاب بـ", "أعراضي تشير إلى إصابتي بـ",
    "نتيجة التشخيص هي", "تقرير الطبيب يشير إلى أنني أعاني من", "تقرير الطبيب أثبت إصابتي بـ",
    "تشخيص الحالة الحالية هو", "تشخيص الحالة النهائية يشير إلى إصابتي بـ"
]

# Initialize statistics dictionary
stats = defaultdict(lambda: {"count": 0, "user_ids": []})

# List to store matching posts
matching_posts = []

# Function to scan JSONL files for matching posts with progress updates
def scan_jsonl_files_for_keywords(folder_path, char_range=40):
    files = [f for f in os.listdir(folder_path) if f.endswith('.jsonl')]  # Filter JSONL files
    for filename in tqdm(files, desc="Processing Files"):  # Live update for files
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in tqdm(lines, desc=f"Inspecting lines in {filename}", leave=False):
                try:
                    post = json.loads(line)  # Parse each line as JSON
                    check_post_for_proximity(post, filename, char_range)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file: {filename}")

# Function to check proximity of diagnosis phrases and keywords
def check_post_for_proximity(post, source_file, char_range):
    title = post.get('title', '')
    selftext = post.get('selftext', '')
    user_id = post.get('author', 'unknown')
    subreddit = post.get('subreddit', 'unknown')
    post_id = post.get('id', 'unknown')

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
                        
                        # Save matching post details
                        matching_posts.append({
                            "user_id": user_id,
                            "post_id": post_id,
                            "subreddit": subreddit,
                            "matched_keyword": keyword,
                            "title": title,
                            "selftext": selftext
                        })
                        return  # Stop further checks for this post once a match is found

# Specify the folder containing JSONL files
folder_path = "../nono_arctic"  # Replace with your folder path

# Scan the folder for matching posts with a proximity range of 40 characters
scan_jsonl_files_for_keywords(folder_path, char_range=40)

# Save stats to a JSON file
output_stats_file = "matching_stats.json"
with open(output_stats_file, 'w', encoding='utf-8') as stats_file:
    json.dump(stats, stats_file, ensure_ascii=False, indent=4)

print(f"Matching statistics saved to {output_stats_file}")

# Save matching posts to a separate JSON file
output_matches_file = "matching_posts.json"
with open(output_matches_file, 'w', encoding='utf-8') as matches_file:
    json.dump(matching_posts, matches_file, ensure_ascii=False, indent=4)

print(f"Matching posts saved to {output_matches_file}")