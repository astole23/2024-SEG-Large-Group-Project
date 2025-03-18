
// Mock data for demonstration
const mockJobs = [
    { 
      title: 'React Developer',
      company: 'Apple',
      location: 'Cupertino, CA',
      salary: '$120k - $180k'
    },
    { 
      title: 'Frontend Engineer',
      company: 'Meta',
      location: 'Remote',
      salary: '$130k - $190k'
    },
    { 
      title: 'Full Stack Developer',
      company: 'Amazon',
      location: 'Seattle, WA',
      salary: '$140k - $200k'
    }
  ];
  
  // Mock CV data
  const userCVScript = document.getElementById('cv-data');
  const mockCV = userCVScript ? JSON.parse(userCVScript.textContent) : {};
  console.log("Loaded CV from backend:", mockCV);

  console.log("Loaded CV data:", mockCV); //  Optional: Helps you debug what’s coming in
  // Raw CV file info (for filename, URL, timestamp)
  const rawCVScript = document.getElementById('cv-raw-info');
  let rawCVInfo = rawCVScript ? JSON.parse(rawCVScript.textContent) : {};

  console.log("📄 Raw CV Info:", rawCVInfo);


  // Function to fetch job postings from the API (or use a fallback)
  function fetchJobPostings() {
    // If you have an API endpoint, use it. Otherwise, fall back to mock data.
    return fetch('/api/job_postings/')
      .then(response => response.json())
      .catch(error => {
        console.error('Error fetching job postings:', error);
        // Fallback: use the existing mockJobs data
        return [
          { id: 1, job_title: 'React Developer', company_name: 'Apple', location: 'Cupertino, CA', salary_range: '$120k - $180k', contract_type: 'Full-time', job_overview: 'Develop user interfaces...', roles_responsibilities: 'Build components, debug code...', required_skills: 'React, JavaScript' },
          { id: 2, job_title: 'Frontend Engineer', company_name: 'Meta', location: 'Remote', salary_range: '$130k - $190k', contract_type: 'Contract', job_overview: 'Design modern web apps...', roles_responsibilities: 'UI design, testing...', required_skills: 'HTML, CSS, JS' },
          { id: 3, job_title: 'Full Stack Developer', company_name: 'Amazon', location: 'Seattle, WA', salary_range: '$140k - $200k', contract_type: 'Full-time', job_overview: 'Work across the stack...', roles_responsibilities: 'API design, integration...', required_skills: 'Python, React, SQL' }
        ];
        });
      };
  

  function renderJobListings(jobs) {
    const listingsContainer = document.getElementById('temporary-job-listings-container');
    listingsContainer.innerHTML = ''; // Clear any existing content

    jobs.forEach(job => {
      // Create a job card similar to the employer grid
      const card = document.createElement('div');
      card.className = 'job-card';
      card.innerHTML = `
        <h5 class="job-title">${job.job_title}</h5>
        <p class="company-name">${job.company_name}</p>
        <p class="location"><span>📍</span> ${job.location}</p>
        <p class="pay-contract">${job.salary_range} | ${job.contract_type}</p>
        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#jobModal${job.id}">
          View &amp; Apply
        </button>
      `;
      listingsContainer.appendChild(card);

      // Create a corresponding modal for job details
      const modalDiv = document.createElement('div');
      modalDiv.className = 'modal fade';
      modalDiv.id = `jobModal${job.id}`;
      modalDiv.tabIndex = -1;
      modalDiv.setAttribute('aria-labelledby', `jobModalLabel${job.id}`);
      modalDiv.setAttribute('aria-hidden', 'true');
      modalDiv.innerHTML = `
        <div class="modal-dialog modal-dialog-scrollable modal-lg">
          <div class="modal-content">
            <div class="modal-header" style="background-color: var(--primary-color); color: white;">
              <h5 class="modal-title" id="jobModalLabel${job.id}">${job.job_title}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="alert alert-info alert-dismissible fade show" id="cvStatusAlert" style="display: none;" role="alert">
              <span id="cvStatusMessage">Status message here</span>
              <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <p><strong>Company:</strong> ${job.company_name}</p>
              <p><strong>Location:</strong> ${job.location}</p>
              <p><strong>Salary:</strong> ${job.salary_range}</p>
              <p><strong>Contract:</strong> ${job.contract_type}</p>
              <p><strong>Job Overview:</strong> ${job.job_overview}</p>
              <p><strong>Roles &amp; Responsibilities:</strong> ${job.roles_responsibilities}</p>
              <p><strong>Required Skills:</strong> ${job.required_skills}</p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <a href="/apply/start/${job.id}/" class="btn btn-primary">Apply Now</a>
            </div>
          </div>
        </div>
      `;
      // Append modal to body (or another container outside the dashboard if preferred)
      document.body.appendChild(modalDiv);
    });
  }



  // Assuming you have a way to get the documents data in JavaScript
  const documentsData = []; // Replace with actual data fetching logic
  function createDashboard() {
    
    console.log("🧾 Raw CV being used in dashboard:", rawCVInfo);



    // Grab the script tag with id="current-user"
    const userInfoScript = document.getElementById('current-user');
    const userInfo = userInfoScript ? JSON.parse(userInfoScript.textContent) : {};
    console.log("Dashboard is loading");
    console.log("User info:", userInfo);

    // Inside createDashboard()

  

    const app = document.querySelector('#app');
    app.innerHTML = `
      <div class="dashboard">
        <main>
          <section class="profile-section">
            <div class="profile-picture">
              <img src="https://i.pravatar.cc/128" alt="John Doe" width="64" height="64">
            </div>
            <div class="profile-info">
              <h1>${userInfo.full_name}</h1>
              <p>Senior Software Developer</p>
              <div class="location">
                <span>📍</span>
                San Francisco, CA
              </div>
            </div>
            <button class="btn-outline">Edit Profile</button>
          </section>
  
          <section class="cv-section">
            <div class="section-header" id="cvToggle">
              <h2>CV</h2>
              <span class="toggle-icon">▼</span>
            </div>
            <div class="cv-content" id="cvContent">
              <!-- PDF CV Section -->
              <div class="document-item">
                <span class="document-icon">📄</span>
                <div class="document-info">
                  <h3>${rawCVInfo.filename || 'No CV uploaded yet'}</h3>
                  <p>Updated ${rawCVInfo.uploaded_at || 'N/A'}</p>


                </div>
                <div class="document-actions" id="cvDocumentActionsPlaceholder"></div>

              </div>
              </div>
              <div class="upload-section">
                <p>Update your CV (PDF only)</p>
                <input type="file" id="cvUpload" accept=".pdf" style="display: none">
                <button class="btn btn-primary" id="uploadRawCvBtn">Upload CV</button>
              </div>
  
              <!-- Online CV Section -->
              <div class="online-cv-section">
                <h3>Online CV</h3>
                <div class="cv-preview">
                  <div class="cv-section">
                    <h4>Personal Information</h4>
                    <p><strong>Name:</strong> ${mockCV.personalInfo?.fullName || 'N/A'}</p>
                    <p><strong>Email:</strong> ${mockCV.personalInfo?.email  || 'N/A'}</p>
                    <p><strong>Phone:</strong> ${mockCV.personalInfo?.phone  || 'N/A'}</p>
                    <p><strong>Address:</strong> ${mockCV.personalInfo?.address  || 'N/A'}</p>
                  </div>
                  <div class="cv-section">
                    <h4>Education</h4>
                    ${(mockCV.education || []).map(edu => `
                      <div class="education-entry">
                        <p><strong>University:</strong> ${edu.university  || 'N/A'}</p>
                        <p><strong>Degree:</strong> ${edu.degreeType} in ${edu.fieldOfStudy  || 'N/A'}</p>
                        <p><strong>Grade:</strong> ${edu.grade  || 'N/A'}</p>
                        <p><strong>Period:</strong> ${edu.dates  || 'N/A'}</p>
                      </div>
                    `).join('')}
                  </div>
                  <div class="cv-section">
                    <h4>Work Experience</h4>
                    ${(mockCV.workExperience || []).map(exp =>  `
                      <div class="experience-entry">
                        <p><strong>Role:</strong> ${exp.jobTitle  || 'N/A'}</p>
                        <p><strong>Company:</strong> ${exp.employer  || 'N/A'}</p>
                        <p><strong>Period:</strong> ${exp.dates  || 'N/A'}</p>
                        <p><strong>Responsibilities:</strong> ${exp.responsibilities  || 'N/A'}</p>
                      </div>
                    `).join('')}
                  </div>
                  <div class="cv-section">
                    <h4>Skills</h4>
                    <div><strong>Technical:</strong>
                      <ul>
                        ${(mockCV.skills?.technicalSkills || '')
                          .split(',')
                          .filter(s => s.trim())
                          .map(skill => `<li>${skill.trim()}</li>`).join('')}
                      </ul>
                    </div>
                    <div><strong>Key Skills:</strong>
                      <ul>
                        ${(mockCV.skills?.keySkills || '')
                          .split(',')
                          .filter(s => s.trim())
                          .map(skill => `<li>${skill.trim()}</li>`).join('')}
                      </ul>
                    </div>
                    <div><strong>Languages:</strong>
                      <ul>
                        ${(mockCV.skills?.languages || '')
                          .split(',')
                          .filter(s => s.trim())
                          .map(lang => `<li>${lang.trim()}</li>`).join('')}
                      </ul>
                    </div>
                  </div>

                </div>
                <button class="btn btn-primary" id="editCVBtn">Edit Online CV</button>
              </div>
            </div>
          </section>
  
       
          <div class="modal-header">
            <h2>📑 Supporting Documents / Certificates</h2>

          </div>
          <div class="upload-section">
            <p>Upload additional documents</p>
            <input type="file" id="docUpload" style="display: none">
            <button class="btn btn-primary" id="docUploadBtn">Upload Document</button>
          </div>
     
  
          <section class="application-progress">
            <div class="progress-header">
              <div class="company-info">
                <h2>Google</h2>
                <p>Senior Frontend Developer</p>
              </div>
              <span class="status-badge">Interview</span>
            </div>
            <div class="progress-steps">
              <div class="progress-line"></div>
              <div class="step active">
                <div class="step-dot">✓</div>
                <div class="step-label">Applied</div>
              </div>
              <div class="step active">
                <div class="step-dot">✓</div>
                <div class="step-label">Screening</div>
              </div>
              <div class="step active">
                <div class="step-dot">•</div>
                <div class="step-label">Interview</div>
              </div>
              <div class="step">
                <div class="step-dot">•</div>
                <div class="step-label">Offer</div>
              </div>
            </div>
          </section>
        </main>
  
        <aside>
          <section class="suggested-jobs">
            <h2>Suggested Jobs</h2>
            <div id="suggested-jobs"></div>
            <a href="#" class="view-all">View all suggestions</a>
          </section>
          <div class="quick-actions">
            <button class="btn btn-primary" id="uploadAutoCvBtn">Autofill CV</button>

            <button class="btn btn-outline" id="browseJobsBtn">Browse Jobs</button>
            <button class="btn btn-outline" id="viewApplicationsBtn">My Applications</button>

          </div>
        </aside>
      </div>

      <!-- Temporary section for testing available job listings -->
      <section class="temporary-job-listings">
        <h2>Available Job Listings (Temporary)</h2>
        <div id="temporary-job-listings-container"></div>
      </section>
  
      <!-- CV Edit Modal -->
      <div id="cvModal" class="modal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>Edit Online CV</h2>
            <span class="close-modal">&times;</span>
          </div>
          <form id="cvForm" class="cv-form">
            <div class="form-section">
              <h3>1. Personal Information</h3>
              <div class="form-group">
                <label for="fullName">Full Name</label>
                <input type="text" id="fullName" name="fullName" required>
              </div>
              <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" name="email" required>
              </div>
              <div class="form-group">
                <label for="phone">Phone Number</label>
                <input type="tel" id="phone" name="phone" required>
              </div>
              <div class="form-group">
                <label for="address">Current Address (including postcode)</label>
                <input type="text" id="address" name="address" required>
              </div>
            </div>
  
            <div class="form-section">
              <h3>2. Right to Work</h3>
              <div class="form-group">
                <label>Do you have the right to work in the UK?</label>
                <div class="radio-group">
                  <input type="radio" id="rightToWorkYes" name="rightToWork" value="Yes">
                  <label for="rightToWorkYes">Yes</label>
                  <input type="radio" id="rightToWorkNo" name="rightToWork" value="No">
                  <label for="rightToWorkNo">No</label>
                </div>
              </div>
              <div class="form-group">
                <label for="visaDetails">Visa details (type, expiry date) (if applicable)</label>
                <input type="text" id="visaDetails" name="visaDetails">
              </div>
            </div>
  
            <div class="form-section">
              <h3>3. Education</h3>
              <div id="educationEntries">
                <!-- Education entries will be dynamically added here -->
              </div>
              <button type="button" class="btn btn-outline" id="addEducation">+ Add Education</button>
            </div>
  
            <div class="form-section">
              <h3>4. Work Experience</h3>
              <div id="workExperienceEntries">
                <!-- Work experience entries will be dynamically added here -->
              </div>
              <button type="button" class="btn btn-outline" id="addWorkExperience">+ Add Work Experience</button>
            </div>
  
            <div class="form-section">
              <h3>5. Skills</h3>
              <div class="form-group">
                <label for="keySkills">Key Skills</label>
                <textarea id="keySkills" name="keySkills" placeholder="e.g., communication, teamwork" required></textarea>
              </div>
              <div class="form-group">
                <label for="technicalSkills">Technical Skills</label>
                <textarea id="technicalSkills" name="technicalSkills" placeholder="e.g., Python, Excel, SQL" required></textarea>
              </div>
              <div class="form-group">
                <label for="languages">Languages</label>
                <textarea id="languages" name="languages" placeholder="e.g., English fluency, other languages"></textarea>
              </div>
            </div>
  
            <div class="form-section">
              <h3>6. Motivation</h3>
              <div class="form-group">
                <label for="interest">Why are you interested in this internship? (250-500 words)</label>
                <textarea id="interest" name="interest" required></textarea>
              </div>
              <div class="form-group">
                <label for="fitForRole">Why are you a good fit for this role? (skills, experiences)</label>
                <textarea id="fitForRole" name="fitForRole" required></textarea>
              </div>
              <div class="form-group">
                <label for="aspirations">Career Aspirations</label>
                <textarea id="aspirations" name="aspirations" required></textarea>
              </div>
            </div>
  
            <div class="form-section">
              <h3>7. Availability</h3>
              <div class="form-group">
                <label for="startDate">Preferred Start Date</label>
                <input type="date" id="startDate" name="startDate" required>
              </div>
              <div class="form-group">
                <label for="duration">Internship Duration</label>
                <input type="text" id="duration" name="duration" placeholder="e.g., 3 months, 6 months" required>
              </div>
              <div class="form-group">
                <label>Willingness to Relocate</label>
                <div class="radio-group">
                  <input type="radio" id="relocateYes" name="relocate" value="Yes">
                  <label for="relocateYes">Yes</label>
                  <input type="radio" id="relocateNo" name="relocate" value="No">
                  <label for="relocateNo">No</label>
                </div>
              </div>
            </div>
  
            <div class="form-section">
              <h3>8. References</h3>
              <div class="form-group">
                <label for="reference1">Reference 1 (Name, Position, Company, Contact Details)</label>
                <textarea id="reference1" name="reference1" required></textarea>
              </div>
              <div class="form-group">
                <label for="reference2">Reference 2 (optional)</label>
                <textarea id="reference2" name="reference2"></textarea>
              </div>
            </div>
  
            <div class="form-section">
              <h3>9. Optional</h3>
              <div class="form-group">
                <label for="equalOpp">Equal Opportunities Monitoring</label>
                <select id="equalOpp" name="equalOpp">
                  <option value="">Prefer not to say</option>
                  <option value="option1">Option 1</option>
                  <option value="option2">Option 2</option>
                </select>
              </div>
            </div>
  
            <div class="form-actions">
              <button type="submit" class="btn btn-primary">Save Changes</button>
              <button type="button" class="btn btn-outline" id="cancelEdit">Cancel</button>
            </div>
          </form>
        </div>
      </div>

    `;

    fetchJobPostings().then(jobs => {
      renderJobListings(jobs);
    });
  
    // Populate suggested jobs
    const suggestedJobsContainer = document.getElementById('suggested-jobs');
    mockJobs.forEach(job => {
      const jobElement = document.createElement('div');
      jobElement.className = 'job-card';
      jobElement.innerHTML = `
        <h3 class="job-title">${job.title}</h3>
        <p class="company-name">${job.company}</p>
        <div class="job-location">
          <span>📍</span>
          ${job.location}
        </div>
        <p class="salary-range">${job.salary}</p>
      `;
      suggestedJobsContainer.appendChild(jobElement);
    });

    const viewApplicationsBtn = document.getElementById('viewApplicationsBtn');
    if (viewApplicationsBtn) {
        viewApplicationsBtn.addEventListener('click', () => {
            window.location.href = '/user/applications/';
        });
    }
    const browseJobsBtn = document.getElementById('browseJobsBtn');
    if (browseJobsBtn) {
      browseJobsBtn.addEventListener('click', () => {
        window.location.href = '/search/';
      });
    }


    const updateCvBtn = document.getElementById('updateCvBtn');
    if (updateCvBtn) {
      updateCvBtn.addEventListener('click', () => {
        document.getElementById('cvUpload').click();  // Trigger file select
      });
    }
    


    // CV section toggle functionality
    const cvToggle = document.getElementById('cvToggle');
    const cvContent = document.getElementById('cvContent');
    const toggleIcon = cvToggle.querySelector('.toggle-icon');
  
    cvToggle.addEventListener('click', () => {
      cvContent.classList.toggle('collapsed');
      toggleIcon.textContent = cvContent.classList.contains('collapsed') ? '▶' : '▼';
    });
  
    // Modal functionality
    const modal = document.getElementById('cvModal');
    
    const editCVBtn = document.getElementById('editCVBtn');
    console.log("📝 Edit CV button clicked - opening modal");
    console.log("Existing CV data:", mockCV);

    if (editCVBtn) {
      editCVBtn.addEventListener('click', () => {
        modal.style.display = 'block';

        // ✅ Full CV form loading logic goes here:
        educationEntries.innerHTML = '';
        workExperienceEntries.innerHTML = '';

        (mockCV.education || []).forEach(edu => {
          educationEntries.insertAdjacentHTML('beforeend', createEducationEntry(edu));
        });

        (mockCV.workExperience || []).forEach(exp => {
          workExperienceEntries.insertAdjacentHTML('beforeend', createWorkExperienceEntry(exp));
        });

        if (mockCV.personalInfo) {
          Object.keys(mockCV.personalInfo).forEach(key => {
            const input = document.getElementById(key);
            if (input) input.value = mockCV.personalInfo[key];
          });
        }

        // You can add more population logic here if needed
      });
    }



    const closeModalBtn = document.querySelector('.close-modal');
    if (closeModalBtn) {
      closeModalBtn.addEventListener('click', () => {
        modal.style.display = 'none';
        console.log("❌ Modal closed via close icon");

      });
}

    const cancelEdit = document.getElementById('cancelEdit');
    if (cancelEdit) {
      cancelEdit.addEventListener('click', () => {
        modal.style.display = 'none';
        console.log("🚫 Modal canceled via Cancel button");

      });
    }

    const cvForm = document.getElementById('cvForm');
    if (cvForm) {
      cvForm.addEventListener('submit', (e) => {
        e.preventDefault();
        showCVStatus("CV updated.", "success");
        modal.style.display = 'none';
      });
    }

    const cvUploadInput = document.getElementById('cvUpload');
    const uploadRawCvBtn = document.getElementById('uploadRawCvBtn');
    const uploadAutoCvBtn = document.getElementById('uploadAutoCvBtn');
  
    let currentUploadMode = '';
  
    if (uploadRawCvBtn) {
      uploadRawCvBtn.addEventListener('click', () => {
        currentUploadMode = 'raw';
        cvUploadInput?.click();
      });
    }
  
    if (uploadAutoCvBtn) {
      uploadAutoCvBtn.addEventListener('click', () => {
        currentUploadMode = 'autofill';
        cvUploadInput?.click();
      });
    }

    if (cvUploadInput) {
      cvUploadInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
    
        const formData = new FormData();
        formData.append('cv', file);
    
        const uploadUrl = currentUploadMode === 'autofill'
          ? '/upload_cv/'
          : '/upload_raw_cv/';
    
        try {
          const res = await fetch(uploadUrl, {
            method: 'POST',
            body: formData,
            headers: {
              'X-CSRFToken': getCSRFToken()
            }
          });
    
          const result = await res.json();
          console.log("📤 Upload result:", result);
    
          if (result.success) {
            showCVStatus("CV uploaded successfully!", "success");
    
            if (currentUploadMode === 'autofill') {
              if (result.data) {
                autofillCVForm(result.data);
              }
            } else {
              // ✅ raw CV upload — update display
              rawCVInfo.filename = result.filename;
              rawCVInfo.uploaded_at = result.uploaded_at;
              rawCVInfo.file_url = result.file_url;
    
              const docInfo = document.querySelector('.document-info');
              if (docInfo) {
                docInfo.querySelector('h3').textContent = rawCVInfo.filename;
                docInfo.querySelector('p').textContent = "Updated just now";
              }
    
              const docActions = document.querySelector('.document-actions');
              if (docActions) {
                docActions.innerHTML = `
                  <button class="btn-outline btn-small" onclick="window.open('${rawCVInfo.file_url}', '_blank')">View</button>
                  <button class="btn-outline btn-small delete-btn" onclick="deleteRawCV()">Delete</button>
                `;
              }
            }
    
          } else {
            showCVStatus(result.error || "Upload failed.", "danger");
          }
    
        } catch (err) {
          console.error("❌ Upload error:", err);
          showCVStatus("Upload error occurred.", "danger");
        }
    
        // Reset input so selecting the same file again triggers change
        cvUploadInput.value = '';
      });
    }
    const cvActionsContainer = document.getElementById('cvDocumentActionsPlaceholder');

    if (rawCVInfo.file_url && cvActionsContainer) {
      cvActionsContainer.innerHTML = `
        <button class="btn-outline btn-small" onclick="window.open('${rawCVInfo.file_url}', '_blank')">View</button>
        <button class="btn-outline btn-small delete-btn" onclick="deleteRawCV()">Delete</button>
      `;
    } else if (cvActionsContainer) {
      cvActionsContainer.innerHTML = `<p style="color: gray;">No file uploaded</p>`;
    }

    
  

  
    // Function to create education entry HTML
    function createEducationEntry(data = {}) {
      const entryId = Date.now();
      return `
        <div class="entry-container" data-id="${entryId}">
          <div class="entry-header">
            <h4>Education Entry</h4>
            <button type="button" class="btn-remove" onclick="removeEntry(this)">Remove</button>
          </div>
          <div class="form-group">
            <label for="university-${entryId}">University/Institution Name</label>
            <input type="text" id="university-${entryId}" name="university" value="${data.university || ''}" required>
          </div>
          <div class="form-group">
            <label for="degreeType-${entryId}">Degree Type</label>
            <input type="text" id="degreeType-${entryId}" name="degreeType" placeholder="e.g., Bachelor's, Master's" value="${data.degreeType || ''}" required>
          </div>
          <div class="form-group">
            <label for="fieldOfStudy-${entryId}">Field of Study</label>
            <input type="text" id="fieldOfStudy-${entryId}" name="fieldOfStudy" value="${data.fieldOfStudy || ''}" required>
          </div>
          <div class="form-group">
            <label for="grade-${entryId}">Expected Grade</label>
            <input type="text" id="grade-${entryId}" name="grade" placeholder="e.g., 2:1, 1st Class Honours" value="${data.grade || ''}">
          </div>
          <div class="form-group">
            <label for="eduDates-${entryId}">Start and End Dates</label>
            <input type="text" id="eduDates-${entryId}" name="eduDates" value="${data.dates || ''}" required>
          </div>
          <div class="form-group">
            <label for="modules-${entryId}">Relevant Modules or Coursework (optional)</label>
            <textarea id="modules-${entryId}" name="modules">${data.modules || ''}</textarea>
          </div>
        </div>
      `;
    }
  
    // Function to create work experience entry HTML
    function createWorkExperienceEntry(data = {}) {
      const entryId = Date.now();
      return `
        <div class="entry-container" data-id="${entryId}">
          <div class="entry-header">
            <h4>Work Experience Entry</h4>
            <button type="button" class="btn-remove" onclick="removeEntry(this)">Remove</button>
          </div>
          <div class="form-group">
            <label for="employer-${entryId}">Employer Name</label>
            <input type="text" id="employer-${entryId}" name="employer" value="${data.employer || ''}" required>
          </div>
          <div class="form-group">
            <label for="jobTitle-${entryId}">Job Title</label>
            <input type="text" id="jobTitle-${entryId}" name="jobTitle" value="${data.jobTitle || ''}" required>
          </div>
          <div class="form-group">
            <label for="workDates-${entryId}">Start and End Dates</label>
            <input type="text" id="workDates-${entryId}" name="workDates" value="${data.dates || ''}" required>
          </div>
          <div class="form-group">
            <label for="responsibilities-${entryId}">Responsibilities and Achievements</label>
            <textarea id="responsibilities-${entryId}" name="responsibilities" required>${data.responsibilities || ''}</textarea>
          </div>
        </div>
      `;
    }
  
    // Add education entry button functionality
    const addEducationBtn = document.getElementById('addEducation');
    const educationEntries = document.getElementById('educationEntries');

    if (addEducationBtn && educationEntries) {
      addEducationBtn.addEventListener('click', () => {
        educationEntries.insertAdjacentHTML('beforeend', createEducationEntry());
      });
    }

  
    // Add work experience entry button functionality
    const addWorkExperienceBtn = document.getElementById('addWorkExperience');
    const workExperienceEntries = document.getElementById('workExperienceEntries');

    if (addWorkExperienceBtn && workExperienceEntries) {
      addWorkExperienceBtn.addEventListener('click', () => {
        workExperienceEntries.insertAdjacentHTML('beforeend', createWorkExperienceEntry());
      });
    }

  
    // Remove entry functionality
    window.removeEntry = function(button) {
      const container = button.closest('.entry-container');
      container.remove();
    };
  
  
    // File upload handling
    const docUploadBtn = document.getElementById('docUploadBtn');
    const docUploadInput = document.getElementById('docUpload');

    if (docUploadInput && docUploadBtn) {
      docUploadBtn.addEventListener('click', () => {
        docUploadInput.click();
      });

      docUploadInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const currentDocs = document.querySelectorAll('.documents-list .document-item');
        if (currentDocs.length >= 5) {
          showCVStatus("You can only upload up to 5 documents.", "danger");
          return;
        }

        const formData = new FormData();
        formData.append('document', file);

        try {
          const res = await fetch('/upload_user_document/', {
            method: 'POST',
            body: formData
          });

          const result = await res.json();
          console.log("📎 Document upload result:", result);

          if (result.success) {
            showCVStatus("Document uploaded!", "success");
            addDocumentToList(file.name, result.uploaded_at);
          } else {
            showCVStatus(result.error || "Upload failed", "danger");
          }
        } catch (err) {
          console.error("❌ Upload failed:", err);
          showCVStatus("Upload error", "danger");
        }
      });
    }

    
    function addDocumentToList(fileName, uploadedAt) {
      const list = document.querySelector('.documents-list');
      const div = document.createElement('div');
      div.className = 'document-item';
      div.innerHTML = `
        <span class="document-icon">📎</span>
        <div class="document-info">
          <h3>${fileName}</h3>
          <p>Updated just now</p>
        </div>
        <div class="document-actions">
          ${rawCVInfo.file_url ? `
            <button class="btn-outline btn-small" onclick="window.open('${rawCVInfo.file_url}', '_blank')">View</button>
            <button class="btn-outline btn-small delete-btn" onclick="deleteRawCV()">Delete</button>
          ` : `<p style="color: gray;">No file uploaded</p>`}
        </div>


      `;
      list.appendChild(div);
    }
    
    async function deleteDocument(fileName, btn) {
      const formData = new FormData();
      formData.append('filename', fileName);
    
      const res = await fetch('/delete_user_document/', {
        method: 'POST',
        body: formData
      });
    
      const result = await res.json();
      if (result.success) {
        showCVStatus("Document deleted", "success");
        btn.closest('.document-item').remove();  // 🧼 removes it from UI
      } else {
        showCVStatus("Delete failed", "danger");
      }
    }
    
    async function deleteRawCV() {
      const confirmDelete = confirm("Are you sure you want to delete your CV?");
      if (!confirmDelete) return;
    
      try {
        const res = await fetch('/delete_raw_cv/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCSRFToken()
          },
        });
    
        const result = await res.json();
    
        if (result.success) {
          showCVStatus("CV deleted successfully.", "success");
        
          // Reset the global rawCVInfo object
          rawCVInfo.filename = '';
          rawCVInfo.uploaded_at = '';
          rawCVInfo.file_url = '';
        
          // Update DOM
          const docInfo = document.querySelector('.document-info');
          if (docInfo) {
            docInfo.querySelector('h3').textContent = "No CV uploaded yet";
            docInfo.querySelector('p').textContent = "Updated N/A";
          }
        
          const docActions = document.querySelector('.document-actions');
          if (docActions) {
            docActions.innerHTML = `<p style="color: gray;">No file uploaded</p>`;
          }
        }
         else {
          showCVStatus(result.error || "Delete failed.", "danger");
        }
      } catch (err) {
        console.error("❌ Error deleting CV:", err);
        showCVStatus("Error deleting CV", "danger");
      }
    }
    

    function autofillCVForm(data) {
      if (!data) return;
    
      console.log("🔄 Autofilling form with data:", data);
    
      // =====================
      // Smart skills splitting
      // =====================
      const rawSkills = data.Skills || '';
      let technicalSkills = '';
      let keySkills = '';
    
      const softSkillMarkers = ["soft skills", "non-technical skills", "transferable skills"];
      let splitFound = false;
    
      softSkillMarkers.forEach(marker => {
        const index = rawSkills.toLowerCase().indexOf(marker);
        if (index !== -1 && !splitFound) {
          technicalSkills = rawSkills.slice(0, index).trim();
          keySkills = rawSkills.slice(index).replace(new RegExp(`${marker}:?`, 'i'), '').trim();
          splitFound = true;
        }
      });
    
      if (!splitFound) {
        technicalSkills = rawSkills;
      }
    
      // =====================
      // Fill skill fields
      // =====================
      document.getElementById('technicalSkills').value = technicalSkills || '';
      document.getElementById('keySkills').value = keySkills || '';
    
      // =====================
      // Languages + Motivation
      // =====================
      document.getElementById('languages').value = data.Languages || '';
      document.getElementById('interest').value = "Autofilled from CV";
      document.getElementById('fitForRole').value = data["Experience & Education"] || '';
      document.getElementById('aspirations').value = data.Projects || '';
    
      // =====================
      // Personal Info (optional, if available)
      // =====================
      // Personal Info (from AI-parsed data)
      if (data.personalInfo) {
        const { fullName, email, phone, address } = data.personalInfo;
        document.getElementById('fullName').value = fullName || '';
        document.getElementById('email').value = email || '';
        document.getElementById('phone').value = phone || '';
        document.getElementById('address').value = address || '';
      }

    
      // =====================
      // Education
      // =====================
      const educationData = data.education || data.Education || [];
      const educationContainer = document.getElementById('educationEntries');
      educationContainer.innerHTML = '';
    
      educationData.forEach(edu => {
        const entryHTML = createEducationEntry(edu);
        educationContainer.insertAdjacentHTML('beforeend', entryHTML);
      });
    
      // =====================
      // Work Experience
      // =====================

      const workData = data.workExperience || data["Work Experience"] || [];

      const workContainer = document.getElementById('workExperienceEntries');
      workContainer.innerHTML = '';
    
      workData.forEach(exp => {
        const entryHTML = createWorkExperienceEntry(exp);
        workContainer.insertAdjacentHTML('beforeend', entryHTML);
      });
    }
    
    function showCVStatus(message, type = "success") {
      const alertBox = document.getElementById("cvStatusAlert");
      const messageSpan = document.getElementById("cvStatusMessage");
    
      if (!alertBox || !messageSpan) {
        alert(message);
        return;
      }
    
      messageSpan.textContent = message;
      alertBox.className = `alert alert-${type} alert-dismissible fade show`;
      alertBox.style.display = "block";
    }
    window.showCVStatus = showCVStatus;

    
    
  
    docUploadBtn.addEventListener('click', () => {
      docUploadInput.click();
    });
  
  
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.style.display = 'none';
      }
    });
  }

  window.deleteRawCV = async function () {
    const confirmDelete = confirm("Are you sure you want to delete your CV?");
    if (!confirmDelete) return;
  
    try {
      const res = await fetch('/delete_raw_cv/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCSRFToken()  // make sure this works
        },
      });
  
      const result = await res.json();
  
      if (result.success) {
        showCVStatus("CV deleted successfully.", "success");
  
        // Reset display
        const docInfo = document.querySelector('.document-info');
        if (docInfo) {
          docInfo.querySelector('h3').textContent = "No CV uploaded yet";
          docInfo.querySelector('p').textContent = "Updated N/A";
        }
  
        const docActions = document.querySelector('.document-actions');
        if (docActions) {
          docActions.innerHTML = `<p style="color: gray;">No file uploaded</p>`;
        }
  
      } else {
        showCVStatus(result.error || "Delete failed.", "danger");
      }
    } catch (err) {
      console.error("❌ Error deleting CV:", err);
      showCVStatus("Error deleting CV", "danger");
    }
  };

  function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.startsWith(name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return '';
  }
  
  


  document.addEventListener('DOMContentLoaded', () => {
    // Safely parse rawCVInfo from the script tag
    const rawCVScript = document.getElementById('cv-raw-info');
    let rawCVInfo = {};
  
    try {
      rawCVInfo = rawCVScript ? JSON.parse(rawCVScript.textContent) : {};
      console.log("🧾 Loaded real rawCVInfo from backend:", rawCVInfo);
    } catch (err) {
      console.warn("⚠️ Failed to parse rawCVInfo. Using empty fallback.");
      rawCVInfo = {};
    }
  
    // Store it globally for the rest of the dashboard to use
    window.rawCVInfo = rawCVInfo;
  
    // Now build the dashboard
    createDashboard();
  });
  
  
  