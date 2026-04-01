"""Temporary script to inspect the combined data."""
import pandas as pd

df = pd.read_csv('output_data/combined_all_years.csv', dtype=str)

# Check which assessments/grades per year
for year in sorted(df['Year'].unique()):
    yr = df[df['Year'] == year]
    assessments = sorted(yr['Assessment Name'].dropna().unique())
    grades = sorted(yr['Tested Grade/Subject'].dropna().unique())
    print(f"Year {year}: Assessments={assessments}")
    print(f"  Grades: {grades}")
    print()

# Check Stuart-Hobson 'All' students by grade
sh = df[
    (df['School Name'].str.contains('Stuart', na=False, case=False))
    & (df['Student Group Value'] == 'All')
]
print("Stuart-Hobson 'All' students by Year/Grade/Subject:")
cols = ['Year', 'Tested Grade/Subject', 'Subject', 'Assessment Name', 'Percent', 'Count', 'Total Count']
subset = sh[cols].sort_values(['Year', 'Subject', 'Tested Grade/Subject'])
for _, row in subset.iterrows():
    grade = row['Tested Grade/Subject']
    print(f"  {row['Year']} | {str(grade):15} | {row['Subject']:5} | {str(row['Assessment Name']):8} | Pct={str(row['Percent']):>8} | N={row['Total Count']}")

print()
# Now check with individual grade levels matching the manual example  
# Manual example has Grade 06, 07, 08 for SY21-22 and SY22-23
sh_grade = df[
    (df['School Name'].str.contains('Stuart', na=False, case=False))
    & (df['Subject'] == 'ELA')
    & (df['Student Group Value'] == 'All')
    & (df['Tested Grade/Subject'].str.contains('Grade [678]', na=False, regex=True))
]
print("Stuart-Hobson ELA Grade 6/7/8 'All' students:")
for _, row in sh_grade[cols].sort_values(['Year', 'Tested Grade/Subject']).iterrows():
    print(f"  {row['Year']} | {str(row['Tested Grade/Subject']):15} | {row['Assessment Name']:8} | Pct={str(row['Percent']):>8} | Count={row['Count']} / {row['Total Count']}")
