console.log("job_form_validation.js: top-level code is running!");

document.addEventListener('DOMContentLoaded', function() {
  console.log("job_form_validation.js loaded");

  const form = document.getElementById('createJobForm');
  if (!form) {
    console.error("Form with id 'createJobForm' not found.");
    return;
  }
  console.log("Form found, attaching submit event listener.");

  // Attach submit event listener to the form.
  form.addEventListener('submit', function(e) {
    e.preventDefault(); 
    console.log("Form submit event triggered.");

    const errors = validateForm();

    if (errors.length > 0) {
      alert("Please fix the following errors:\n" + errors.join("\n"));
      return;
    }

    const formData = gatherFormData();
    console.log("Validation passed. Submitting AJAX request with data:", formData);

    submitFormData(formData);
  });

  function validateField(fieldId, validationFn) {
    const value = document.getElementById(fieldId).value.trim();
    return validationFn(value);
  }

  function validateForm() {
    let errors = [];

    // Add field validation
    errors.push(...validateJobTitle());
    errors.push(...validateCompanyName());
    errors.push(...validateDepartment());
    errors.push(...validateLocation());
    errors.push(...validateWorkType());
    errors.push(...validateSalaryRange());
    errors.push(...validateContractType());
    errors.push(...validateJobOverview());
    errors.push(...validateRolesResponsibilities());
    errors.push(...validateRequiredSkills());
    errors.push(...validatePreferredSkills());
    errors.push(...validateEducationRequired());
    errors.push(...validatePerksBenefits());
    errors.push(...validateApplicationDeadline());
    errors.push(...validateRequiredDocuments());
    errors.push(...validateCompanyOverview());
    errors.push(...validateWhyJoinUs());
    errors.push(...validateCompanyReviews());

    return errors;
  }

  function validateJobTitle() {
    return validateField('jobTitle', value => {
      if (!value) return ["Job Posting Title is required."];
      if (value.length > 100) return ["Job Posting Title must be less than or equal to 100 characters."];
      return [];
    });
  }

  function validateCompanyName() {
    return validateField('companyName', value => {
      if (!value) return ["Company Name is required."];
      if (value.length > 100) return ["Company Name must be less than or equal to 100 characters."];
      return [];
    });
  }

  function validateDepartment() {
    return validateField('department', value => {
      if (value && value.length > 100) return ["Department Name must be less than or equal to 100 characters."];
      return [];
    });
  }

  function validateLocation() {
    return validateField('location', value => {
      if (!value) return ["Location is required."];
      if (value.length > 100) return ["Location must be less than or equal to 100 characters."];
      return [];
    });
  }

  function validateWorkType() {
    return validateField('workType', value => {
      if (!value) return ["Work Type is required."];
      return [];
    });
  }

  function validateSalaryRange() {
    return validateField('salaryRange', value => {
      if (!value) return ["Salary Range is required."];
      return [];
    });
  }

  function validateContractType() {
    return validateField('contractType', value => {
      if (!value) return ["Contract Type is required."];
      return [];
    });
  }

  function validateJobOverview() {
    return validateField('jobOverview', value => {
      if (value.length < 50) return ["Job Overview must be at least 50 characters."];
      if (value.length > 1000) return ["Job Overview cannot exceed 1000 characters."];
      return [];
    });
  }

  function validateRolesResponsibilities() {
    return validateField('rolesResponsibilities', value => {
      if (value.length < 50) return ["Roles/Responsibilities must be at least 50 characters."];
      if (value.length > 2000) return ["Roles/Responsibilities cannot exceed 2000 characters."];
      return [];
    });
  }

  function validateRequiredSkills() {
    return validateField('requiredSkills', value => {
      if (!value) return ["At least one Required Skill must be added."];
      const skillsArr = value.split(',').map(s => s.trim()).filter(Boolean);
      for (let skill of skillsArr) {
        if (skill.length > 50) return ["Each Required Skill must be 50 characters or less."];
      }
      return [];
    });
  }

  function validatePreferredSkills() {
    return validateField('preferredSkills', value => {
      if (value) {
        const prefSkillsArr = value.split(',').map(s => s.trim()).filter(Boolean);
        for (let skill of prefSkillsArr) {
          if (skill.length > 50) return ["Each Preferred Skill must be 50 characters or less."];
        }
      }
      return [];
    });
  }

  function validateEducationRequired() {
    return validateField('educationRequired', value => {
      if (value && value.length > 150) return ["Education Required must be 150 characters or less."];
      return [];
    });
  }

  function validatePerksBenefits() {
    return validateField('perksBenefits', value => {
      if (value.length < 20) return ["Perks and Benefits must be at least 20 characters."];
      if (value.length > 1000) return ["Perks and Benefits cannot exceed 1000 characters."];
      return [];
    });
  }

  function validateApplicationDeadline() {
    return validateField('applicationDeadline', value => {
      if (!value) return ["Application Deadline is required."];
      const deadlineDate = new Date(value);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (deadlineDate < today) return ["Application Deadline must be a future date."];
      return [];
    });
  }

  function validateRequiredDocuments() {
    return validateField('requiredDocuments', value => {
      if (!value) return ["Required Documents field is required."];
      if (value.length > 300) return ["Required Documents cannot exceed 300 characters."];
      return [];
    });
  }

  function validateCompanyOverview() {
    return validateField('companyOverview', value => {
      if (value.length < 50) return ["Company Overview must be at least 50 characters."];
      if (value.length > 2000) return ["Company Overview cannot exceed 2000 characters."];
      return [];
    });
  }

  function validateWhyJoinUs() {
    return validateField('whyJoinUs', value => {
      if (value.length < 50) return ["Why Join Us must be at least 50 characters."];
      if (value.length > 1000) return ["Why Join Us cannot exceed 1000 characters."];
      return [];
    });
  }

  function validateCompanyReviews() {
    return validateField('companyReviews', value => {
      if (value && value.length > 2000) return ["Company Reviews cannot exceed 2000 characters."];
      return [];
    });
  }

  function gatherFormData() {
    return {
      job_title: document.getElementById('jobTitle').value,
      company_name: document.getElementById('companyName').value,
      department: document.getElementById('department').value,
      location: document.getElementById('location').value,
      work_type: document.getElementById('workType').value,
      salary_range: document.getElementById('salaryRange').value,
      contract_type: document.getElementById('contractType').value,
      job_overview: document.getElementById('jobOverview').value,
      roles_responsibilities: document.getElementById('rolesResponsibilities').value,
      required_skills: document.getElementById('requiredSkills').value,
      preferred_skills: document.getElementById('preferredSkills').value,
      education_required: document.getElementById('educationRequired').value,
      perks: document.getElementById('perksBenefits').value,
      application_deadline: document.getElementById('applicationDeadline').value,
      required_documents: document.getElementById('requiredDocuments').value,
      company_overview: document.getElementById('companyOverview').value,
      why_join_us: document.getElementById('whyJoinUs').value,
      company_reviews: document.getElementById('companyReviews').value
    };
  }

  function submitFormData(formData) {
    fetch('/your-job-posting-endpoint/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
      console.log('Job posting created:', data);
      form.reset();
      document.getElementById('requiredSkillsContainer').innerHTML = "";
      document.getElementById('preferredSkillsContainer').innerHTML = "";
      const modalElement = document.getElementById('createJobModal');
      const modal = new bootstrap.Modal(modalElement);
      modal.hide();
      window.location.reload();
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }

  function initTagInput(inputId, containerId, hiddenInputId) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(containerId);
    const hiddenInput = document.getElementById(hiddenInputId);
    let tags = [];

    function updateHiddenInput() {
      hiddenInput.value = tags.join(',');
    }

    function createTagElement(tag) {
      const tagElem = document.createElement('span');
      tagElem.classList.add('badge', 'bg-primary', 'me-1', 'mb-1');
      tagElem.textContent = tag;

      const closeBtn = document.createElement('button');
      closeBtn.type = 'button';
      closeBtn.classList.add('btn-close', 'btn-close-white', 'ms-1');
      closeBtn.style.fontSize = '0.6em';
      closeBtn.addEventListener('click', function() {
        container.removeChild(tagElem);
        tags = tags.filter(t => t !== tag);
        updateHiddenInput();
      });

      tagElem.appendChild(closeBtn);
      return tagElem;
    }

    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        const tag = input.value.trim();
        if (tag !== '' && !tags.includes(tag.toLowerCase())) {
          tags.push(tag.toLowerCase());
          container.appendChild(createTagElement(tag));
          updateHiddenInput();
          input.value = '';
        }
      }
    });
  }

  initTagInput('requiredSkillsInput', 'requiredSkillsContainer', 'requiredSkills');
  initTagInput('preferredSkillsInput', 'preferredSkillsContainer', 'preferredSkills');
});
