const initialEducation = JSON.parse('{{ initial_data.education|default:"[]"|escapejs }}');
const initialExperience = JSON.parse('{{ initial_data.workExperience|default:"[]"|escapejs }}');

// Function to create a generic field (education or experience)
function createField(type, data = {}) {
  const fieldDiv = document.createElement('div');
  fieldDiv.className = `${type}-entry`;
  
  // Dynamically set placeholders and names
  const fields = {
    institution: { placeholder: 'Institution', value: data.university || data.employer_name || '' },
    degree: { placeholder: 'Degree', value: data.degreeType || '' },
    position: { placeholder: 'Position', value: data.job_title || '' },
    start: { placeholder: 'Start Date', value: (data.dates || '').split('-')[0] || '' },
    end: { placeholder: 'End Date', value: (data.dates || '').split('-')[1] || '' },
  };

  fieldDiv.innerHTML = `
    ${Object.keys(fields).map(field => `
      <div class="form-group">
        <input type="text" name="${field}" placeholder="${fields[field].placeholder}" value="${fields[field].value}">
      </div>
    `).join('')}
    <button type="button" class="remove-field">Remove</button>
  `;

  // Attach remove event
  fieldDiv.querySelector('.remove-field').addEventListener('click', () => fieldDiv.remove());
  return fieldDiv;
}

// Function to add an initial field if there is no data
function initializeFields(container, data, type) {
  if (data.length === 0) container.appendChild(createField(type));

  data.forEach(item => container.appendChild(createField(type, item)));
}

// Init education/work sections
const eduContainer = document.getElementById('education-container');
const expContainer = document.getElementById('experience-container');

document.getElementById('add-education-btn').addEventListener('click', () => {
  eduContainer.appendChild(createField('education'));
});

document.getElementById('add-experience-btn').addEventListener('click', () => {
  expContainer.appendChild(createField('experience'));
});

// Initialize fields with pre-filled data or an empty field
initializeFields(eduContainer, initialEducation, 'education');
initializeFields(expContainer, initialExperience, 'experience');

// Skills Section
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
