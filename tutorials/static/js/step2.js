const initialEducation = JSON.parse('{{ initial_data.education|default:"[]"|escapejs }}');
const initialExperience = JSON.parse('{{ initial_data.workExperience|default:"[]"|escapejs }}');

function createEducationField(edu = {}) {
  const eduDiv = document.createElement('div');
  eduDiv.className = 'education-entry';
  eduDiv.innerHTML = `
    <div class="form-group"><input type="text" name="institution" placeholder="Institution" value="${edu.university || ''}"></div>
    <div class="form-group"><input type="text" name="degree" placeholder="Degree" value="${edu.degreeType || ''}"></div>
    <div class="form-group"><input type="text" name="edu_start" placeholder="Start Date" value="${(edu.dates || '').split('-')[0] || ''}"></div>
    <div class="form-group"><input type="text" name="edu_end" placeholder="End Date" value="${(edu.dates || '').split('-')[1] || ''}"></div>
    <button type="button" class="remove-field">Remove</button>
  `;
  eduDiv.querySelector('.remove-field').addEventListener('click', () => eduDiv.remove());
  return eduDiv;
}

function createExperienceField(exp = {}) {
  const expDiv = document.createElement('div');
  expDiv.className = 'experience-entry';
  expDiv.innerHTML = `
    <div class="form-group"><input type="text" name="company_name" placeholder="Company" value="${exp.employer_name || ''}"></div>
    <div class="form-group"><input type="text" name="position" placeholder="Position" value="${exp.job_title || ''}"></div>
    <div class="form-group"><input type="text" name="work_start" placeholder="Start Date" value="${(exp.dates || '').split('-')[0] || ''}"></div>
    <div class="form-group"><input type="text" name="work_end" placeholder="End Date" value="${(exp.dates || '').split('-')[1] || ''}"></div>
    <button type="button" class="remove-field">Remove</button>
  `;
  expDiv.querySelector('.remove-field').addEventListener('click', () => expDiv.remove());
  return expDiv;
}

// Init education/work sections
const eduContainer = document.getElementById('education-container');
const expContainer = document.getElementById('experience-container');

document.getElementById('add-education-btn').addEventListener('click', () => {
  eduContainer.appendChild(createEducationField());
});
document.getElementById('add-experience-btn').addEventListener('click', () => {
  expContainer.appendChild(createExperienceField());
});

// Pre-fill if data exists
initialEducation.forEach(e => eduContainer.appendChild(createEducationField(e)));
initialExperience.forEach(e => expContainer.appendChild(createExperienceField(e)));

// If no data, start with 1 empty row
if (initialEducation.length === 0) eduContainer.appendChild(createEducationField());
if (initialExperience.length === 0) expContainer.appendChild(createExperienceField());


const skillsContainer = document.getElementById('skills-container');
const addSkillBtn = document.getElementById('add-skill-btn');

function createSkillField(skill = '') {
  const div = document.createElement('div');
  div.className = 'skill-entry';
  div.innerHTML = `
    <input type="text" name="skill" placeholder="Enter skill" value="${skill}">
    <button type="button" class="remove-field">Remove</button>
  `;
  div.querySelector('.remove-field').addEventListener('click', () => div.remove());
  return div;
}

addSkillBtn.addEventListener('click', () => {
  skillsContainer.appendChild(createSkillField());
});

if (skillsData.length > 0) {
  skillsData.forEach(skill => skillsContainer.appendChild(createSkillField(skill)));
} else {
  skillsContainer.appendChild(createSkillField());
}


