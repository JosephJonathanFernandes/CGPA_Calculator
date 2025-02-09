import streamlit as st
import matplotlib.pyplot as plt
import webbrowser


Credits = [16, 18, 23, 24, 22, 0, 0, 0]
total_credits = sum(Credits)

st.title('CGPA Calculator')

st.markdown('---')
num_courses = st.number_input('Number of Sems', min_value=1, step=1, value=5)


if st.checkbox('Add Custom Credits'):

    st.write('The default credits for each semester are based on the GEC Computer curriculum. You may customize the credits below as per your requirements:')
    st.subheader('Enter your Custom Credits below:')
    creds = []
    for i in range(num_courses):
        credit = st.number_input(f'Sem {i+1}', min_value=0, step=1, value=Credits[i])
        creds.append(credit)
    Credits = creds
    total_credits = sum(Credits)

st.markdown('---')

st.subheader('Enter your SGPA below:')

grades = []
for i in range(num_courses):
    grade = st.number_input(f'Sem {i+1}', min_value=0.0, max_value=10.0, step=0.1)
    grades.append(grade)

total_grade = sum([a*b for a,b in zip(grades, Credits)])
cgpa = total_grade/total_credits
st.markdown('---')

st.subheader(f'Your CGPA is: {cgpa:.2f}')

gdrive_link = "https://drive.google.com/file/d/1JyIgnGSZpeBphGtcoDdaj8eXnVvROFb8/view?usp=drivesdk"
if st.button('View CGPA Calculation Guide'):
    webbrowser.open_new_tab(gdrive_link)
    
st.markdown('---')
with st.expander("Trend"):
    st.subheader('SGPA Trend')

    fig, ax = plt.subplots()
    ax.plot(range(1, num_courses + 1), grades, marker='o', linestyle='-', color='b')
    ax.set_xlabel('Semester')
    ax.set_ylabel('SGPA')
    ax.set_title('SGPA Trend Over Semesters')
    ax.grid(True)
    ax.set_ylim(0, 10)  # Set y-axis to start from 0 and end at 10
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

    st.pyplot(fig)
# st.write('Made with ❤️ by Akaash Samson')