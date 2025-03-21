// job_form_validation.js

console.log("job_form_validation.js: top-level code is running!");


// job_form_validation.js

document.addEventListener('DOMContentLoaded', function() {
  console.log("job_form_validation.js loaded");

  // Attach submit event listener to the form.
  const form = document.getElementById('createJobForm');
  if (!form) {
    console.error("Form with id 'createJobForm' not found.");
    return;
  }
  console.log("Form found, attaching submit event listener.");

  form.addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent the default form submission
    console.log("Form submit event triggered.");

    let errors = [];

    // Validate Job Posting Title (required, max 100 characters)
    let jobTitle = document.getElementById('jobTitle').value.trim();
    if (!jobTitle) {
      errors.push("Job Posting Title is required.");
    } else if (jobTitle.length > 100) {
      errors.push("Job Posting Title must be less than or equal to 100 characters.");
    }

    // Validate Company Name (required, max 100 characters)
    let companyName = document.getElementById('companyName').value.trim();
    if (!companyName) {
      errors.push("Company Name is required.");
    } else if (companyName.length > 100) {
      errors.push("Company Name must be less than or equal to 100 characters.");
    }

    // Validate Department Name (optional, max 100 characters)
    let department = document.getElementById('department').value.trim();
    if (department && department.length > 100) {
      errors.push("Department Name must be less than or equal to 100 characters.");
    }

    // Validate Location (required, max 100 characters)
    let location = document.getElementById('location').value.trim();
    if (!location) {
      errors.push("Location is required.");
    } else if (location.length > 100) {
      errors.push("Location must be less than or equal to 100 characters.");
    }

    // Validate Work Type (required)
    let workType = document.getElementById('workType').value;
    if (!workType) {
      errors.push("Work Type is required.");
    }

    // Validate Salary Range (required)
    let salaryRange = document.getElementById('salaryRange').value.trim();
    if (!salaryRange) {
      errors.push("Salary Range is required.");
    }

    // Validate Contract Type (required)
    let contractType = document.getElementById('contractType').value;
    if (!contractType) {
      errors.push("Contract Type is required.");
    }

    // Validate Job Overview (required, min 50, max 1000)
    let jobOverview = document.getElementById('jobOverview').value.trim();
    if (jobOverview.length < 50) {
      errors.push("Job Overview must be at least 50 characters.");
    } else if (jobOverview.length > 1000) {
      errors.push("Job Overview cannot exceed 1000 characters.");
    }

    // Validate Roles/Responsibility (required, min 50, max 2000)
    let rolesResponsibilities = document.getElementById('rolesResponsibilities').value.trim();
    if (rolesResponsibilities.length < 50) {
      errors.push("Roles/Responsibilities must be at least 50 characters.");
    } else if (rolesResponsibilities.length > 2000) {
      errors.push("Roles/Responsibilities cannot exceed 2000 characters.");
    }

    // Validate Required Skills (required; check hidden input for comma-separated list)
    let requiredSkills = document.getElementById('requiredSkills').value.trim();
    if (!requiredSkills) {
      errors.push("At least one Required Skill must be added.");
    } else {
      let skillsArr = requiredSkills.split(',').map(s => s.trim()).filter(Boolean);
      skillsArr.forEach(skill => {
        if (skill.length > 50) {
          errors.push("Each Required Skill must be 50 characters or less.");
        }
      });
    }

    // Validate Preferred Skills (optional; if provided, each skill max 50 characters)
    let preferredSkills = document.getElementById('preferredSkills').value.trim();
    if (preferredSkills) {
      let prefSkillsArr = preferredSkills.split(',').map(s => s.trim()).filter(Boolean);
      prefSkillsArr.forEach(skill => {
        if (skill.length > 50) {
          errors.push("Each Preferred Skill must be 50 characters or less.");
        }
      });
    }

    // Validate Education Required (optional, max 150 characters)
    let educationRequired = document.getElementById('educationRequired').value.trim();
    if (educationRequired && educationRequired.length > 150) {
      errors.push("Education Required must be 150 characters or less.");
    }

    // Validate Perks and Benefits (required, min 20, max 1000)
    let perksBenefits = document.getElementById('perksBenefits').value.trim();
    if (perksBenefits.length < 20) {
      errors.push("Perks and Benefits must be at least 20 characters.");
    } else if (perksBenefits.length > 1000) {
      errors.push("Perks and Benefits cannot exceed 1000 characters.");
    }

    // Validate Application Deadline (required, must be a future date)
    let applicationDeadline = document.getElementById('applicationDeadline').value;
    if (!applicationDeadline) {
      errors.push("Application Deadline is required.");
    } else {
      let deadlineDate = new Date(applicationDeadline);
      let today = new Date();
      today.setHours(0, 0, 0, 0);
      if (deadlineDate < today) {
        errors.push("Application Deadline must be a future date.");
      }
    }

    // Validate Required Documents (required, max 300 characters)
    let requiredDocuments = document.getElementById('requiredDocuments').value.trim();
    if (!requiredDocuments) {
      errors.push("Required Documents field is required.");
    } else if (requiredDocuments.length > 300) {
      errors.push("Required Documents cannot exceed 300 characters.");
    }

    // Validate Company Overview (required, min 50, max 2000)
    let companyOverview = document.getElementById('companyOverview').value.trim();
    if (companyOverview.length < 50) {
      errors.push("Company Overview must be at least 50 characters.");
    } else if (companyOverview.length > 2000) {
      errors.push("Company Overview cannot exceed 2000 characters.");
    }

    // Validate Why Join Us? (required, min 50, max 1000)
    let whyJoinUs = document.getElementById('whyJoinUs').value.trim();
    if (whyJoinUs.length < 50) {
      errors.push("Why Join Us must be at least 50 characters.");
    } else if (whyJoinUs.length > 1000) {
      errors.push("Why Join Us cannot exceed 1000 characters.");
    }

    // Validate Company Reviews (optional, max 2000 characters)
    let companyReviews = document.getElementById('companyReviews').value.trim();
    if (companyReviews && companyReviews.length > 2000) {
      errors.push("Company Reviews cannot exceed 2000 characters.");
    }

    // If there are errors, alert them and stop submission.
    if (errors.length > 0) {
      alert("Please fix the following errors:\n" + errors.join("\n"));
      return;
    }

    // Gather form data for AJAX submission.
    const formData = {
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

    console.log("Validation passed. Submitting AJAX request with data:", formData);

    // Submit the data via AJAX
    fetch('/your-job-posting-endpoint/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(formData)
    })
    .then(response => {
      console.log("Received response status:", response.status);
      return response.json();
    })
    .then(data => {
      console.log('Job posting created:', data);
      // Reset the form and clear any tag containers
      form.reset();
      document.getElementById('requiredSkillsContainer').innerHTML = "";
      document.getElementById('preferredSkillsContainer').innerHTML = "";
      // Close the modal after successful submission
      const modalElement = document.getElementById('createJobModal');
      const modal = new bootstrap.Modal(modalElement);
      modal.hide();
      window.location.reload();
    })
    
    .catch(error => {
      console.error('Error:', error);
    });
  });

  // Initialize tag inputs
  function initTagInput(inputId, containerId, hiddenInputId) {
    const input = document.getElementById(inputId);
    const container = document.getElementById(containerId);
    const hiddenInput = document.getElementById(hiddenInputId);
    let tags = [];

    // Update the hidden input with the current tags list.
    function updateHiddenInput() {
      hiddenInput.value = tags.join(',');
    }

    // Create a badge element for a tag.
    function createTagElement(tag) {
      const tagElem = document.createElement('span');
      tagElem.classList.add('badge', 'bg-primary', 'me-1', 'mb-1');
      tagElem.textContent = tag;

      // Create a close button for the tag.
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

    // Listen for Enter key presses to add a new tag.
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

  // Initialize the tag inputs on DOM load
  initTagInput('requiredSkillsInput', 'requiredSkillsContainer', 'requiredSkills');
  initTagInput('preferredSkillsInput', 'preferredSkillsContainer', 'preferredSkills');
});
