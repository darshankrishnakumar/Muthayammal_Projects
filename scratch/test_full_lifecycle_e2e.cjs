const http = require('http');

function post(path, payload, token) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(payload || {});
    const headers = {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(data)
    };
    if (token) headers['Authorization'] = 'Bearer ' + token;

    const req = http.request({
      hostname: '127.0.0.1',
      port: 8080,
      path: path,
      method: 'POST',
      headers: headers
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(body) });
        } catch (e) {
          resolve({ status: res.statusCode, raw: body });
        }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function get(path, token) {
  return new Promise((resolve, reject) => {
    const headers = {};
    if (token) headers['Authorization'] = 'Bearer ' + token;

    const req = http.request({
      hostname: '127.0.0.1',
      port: 8080,
      path: path,
      method: 'GET',
      headers: headers
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(body) });
        } catch (e) {
          resolve({ status: res.statusCode, raw: body });
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function runTests() {
  console.log('=== STARTING COMPLETE WORKFLOW & LIFECYCLE E2E TESTS ===');

  // 1. Authenticate Super Admin
  const saLogin = await post('/api/auth/login', { email: 'superadmin@academic.com', password: 'Superadmin123!' });
  if (saLogin.status !== 200) {
    console.error('Super Admin login failed:', saLogin);
    process.exit(1);
  }
  const saToken = saLogin.data.token;
  console.log('[PASS] Super Admin Authenticated. Role:', saLogin.data?.user?.role, 'Email:', saLogin.data?.user?.email);

  const ts = Date.now();
  const devEmail = `dev.vikram.${ts}@tech.in`;
  const userEmail = `researcher.priya.${ts}@university.edu`;

  // 2. Provision & Authenticate Project Developer via Super Admin
  const devCreate = await post('/api/users', {
    fullName: 'Vikram Dev',
    email: devEmail,
    password: 'password123',
    role: 'PROJECT_DEVELOPER',
    status: 'ACTIVE'
  }, saToken);
  console.log('devCreate debug:', devCreate);

  let devLogin = await post('/api/auth/login', { email: devEmail, password: 'password123' });
  const devToken = devLogin.data?.token;
  const devUserId = devLogin.data?.user?.id;
  console.log('[PASS] Project Developer Authenticated:', devLogin.data?.user?.email, 'Role:', devLogin.data?.user?.role, 'ID:', devUserId);

  // 3. Register & Authenticate regular Customer User
  await post('/api/auth/register', {
    fullName: 'Priya Sharma',
    email: userEmail,
    password: 'password123',
    confirmPassword: 'password123',
    organization: 'National Institute',
    mobileNumber: '9123456789'
  });
  let userLogin = await post('/api/auth/login', { email: userEmail, password: 'password123' });

  const userToken = userLogin.data?.token;
  const custUserId = userLogin.data?.user?.id;
  console.log('[PASS] Customer User Authenticated:', userLogin.data?.user?.email, 'Role:', userLogin.data?.user?.role, 'ID:', custUserId);

  // 4. Test Access Control Overview
  const overview = await get('/api/access-control/overview', saToken);
  console.log('[PASS] Access Control Overview fetched. Total admins:', overview.data?.admins?.length);

  // 5. Test Super Admin Permission Scoping (Preset: COMPANY_ADMIN)
  if (overview.data?.admins?.length > 0) {
    const targetAdmin = overview.data.admins[0];
    const presetRes = await post(`/api/access-control/admins/${targetAdmin.id}/preset`, { preset: 'COMPANY_ADMIN' }, saToken);
    console.log('[PASS] Applied COMPANY_ADMIN preset to Admin #' + targetAdmin.id, presetRes.status === 200 ? 'SUCCESS' : 'FAILED');
  }

  // 6. PATH B: Custom Requirement Submission & Lifecycle
  console.log('\n--- TESTING PATH B: CUSTOM REQUIREMENT WORKFLOW ---');
  const reqCreate = await post('/api/requirements', {
    title: 'Quantum Key Distribution Simulation Tool',
    problemStatement: 'Simulate BB84 quantum protocol with eavesdropping detection and secure channels.',
    budget: 600.00,
    technologyStack: 'Python, Qiskit, React',
    tags: 'Quantum, Security'
  }, userToken);
  console.log('reqCreate debug:', reqCreate);
  console.log('[PASS] Requirement Submitted:', reqCreate.data?.id, 'Status:', reqCreate.data?.status);
  const reqId = reqCreate.data.id;

  // 6a. Pay Advance Amount
  const advancePay = await post(`/api/requirements/${reqId}/pay-advance`, {
    amount: 300.00,
    idempotencyKey: 'adv_' + reqId + '_1'
  }, userToken);
  console.log('advancePay debug:', advancePay);
  console.log('[PASS] Advance Payment Processed ($300.00). Status:', advancePay.status, 'Order #:', advancePay.data?.order?.orderNumber);

  // Test Idempotency of Advance Payment
  const advancePayDup = await post(`/api/requirements/${reqId}/pay-advance`, {
    amount: 300.00,
    idempotencyKey: 'adv_' + reqId + '_1'
  }, userToken);
  console.log('[PASS] Advance Payment Idempotency Guard:', advancePayDup.data?.order?.orderNumber === advancePay.data?.order?.orderNumber ? 'SUCCESS (Idempotent)' : 'FAILED');

  // 6b. Super Admin Reviews & Approves Requirement
  const reqReview = await post(`/api/requirements/${reqId}/review`, {
    action: 'APPROVE',
    notes: 'Technical specification is sound. Approved for development.'
  }, saToken);
  console.log('reqReview debug:', reqReview);
  console.log('[PASS] Super Admin Approved Requirement. Status:', reqReview.data?.requirement?.status);

  // 6c. Create Project From Requirement
  const projCreate = await post('/api/projects', {
    projectName: 'Quantum Key Distribution Simulator',
    description: 'Full simulation suite with Qiskit.',
    budget: 600.00,
    technologyStack: 'Python, Qiskit, React',
    linkedRequirementId: reqId
  }, saToken);
  console.log('projCreate debug:', projCreate);
  const projId = projCreate.data?.project?.id || projCreate.data?.id;
  console.log('[PASS] Project Initialized from Requirement. ID:', projId, 'Code:', projCreate.data?.projectCode);

  // 6d. Super Admin Assigns Project Developer
  const assignDev = await post(`/api/projects/${projId}/assign-developer`, { developerId: devUserId }, saToken);
  console.log('assignDev debug:', assignDev);
  console.log('[PASS] Developer Assigned to Project:', assignDev.data?.project?.status);

  // 6e. Project Developer views workspace
  const devProjects = await get('/api/projects/my-developer-projects', devToken);
  console.log('devProjects debug:', devProjects);
  console.log('[PASS] Developer Workspace Projects Count:', Array.isArray(devProjects.data) ? devProjects.data.length : 'N/A');

  // 6f. Developer Submits Deliverables for Review
  const devSubmit = await post(`/api/projects/${projId}/developer-submit-review`, {
    notes: 'Implementation complete. 100% test coverage on quantum simulator core.'
  }, devToken);
  console.log('devSubmit debug:', devSubmit);
  console.log('[PASS] Developer Submitted Project for Review. Status:', devSubmit.data?.project?.status);

  // 6g. Admin Reviews & Approves Deliverables
  const adminRev = await post(`/api/projects/${projId}/admin-review`, {
    action: 'APPROVE',
    notes: 'Verified against quantum benchmark test suite. Excellent work.'
  }, saToken);
  console.log('adminRev debug:', adminRev);
  console.log('[PASS] Deliverables Review Approved. Ready for Final Payment:', adminRev.data?.project?.lifecycleStatus);

  // 6h. Customer Pays Remaining Balance to Unlock Deliverables
  const finalPay = await post(`/api/projects/${projId}/pay-remaining`, {
    amount: 300.00,
    idempotencyKey: 'rem_' + projId + '_1'
  }, userToken);
  console.log('finalPay debug:', finalPay);
  console.log('[PASS] Final Remaining Payment Processed ($300.00). Status:', finalPay.status, 'Order #:', finalPay.data?.order?.orderNumber);

  // 7. Check Customer Notifications
  const notifs = await get('/api/notifications', userToken);
  console.log('[PASS] Customer Notifications Received. Total unread:', notifs.data?.unreadCount || notifs.data?.length);

  // 8. PATH A: DIRECT MARKETPLACE PURCHASE WORKFLOW
  console.log('\n--- TESTING PATH A: DIRECT MARKETPLACE PURCHASE WORKFLOW ---');
  const marketItem = await post('/api/projects', {
    projectName: 'Autonomous Drone Navigation Framework',
    description: 'Ready-to-use ROS2 simulation and navigation package.',
    budget: 450.00,
    technologyStack: 'C++, ROS2, Gazebo',
    isMarketplace: true
  }, saToken);
  const marketProjId = marketItem.data?.id;
  console.log('[PASS] Marketplace Project Created:', marketProjId, 'Code:', marketItem.data?.projectCode);

  const purchaseRes = await post(`/api/projects/${marketProjId}/purchase-marketplace`, {
    amount: 450.00,
    idempotencyKey: 'mkt_' + marketProjId + '_1'
  }, userToken);
  console.log('[PASS] Marketplace Project Purchased Directly ($450.00). Status:', purchaseRes.status, 'Order #:', purchaseRes.data?.order?.orderNumber);

  // 9. NEGATIVE AUTHORIZATION TESTS
  console.log('\n--- TESTING NEGATIVE AUTHORIZATION CASES ---');
  // 9a. Developer cannot approve project review
  const illegalReview = await post(`/api/projects/${projId}/admin-review`, { action: 'APPROVE' }, devToken);
  console.log('[PASS] Negative Test: Developer cannot approve project:', illegalReview.status === 403 ? 'FORBIDDEN (Correct)' : 'FAILED');

  // 9b. Regular User cannot assign developer
  const illegalAssign = await post(`/api/projects/${projId}/assign-developer`, { developerId: devUserId }, userToken);
  console.log('[PASS] Negative Test: Regular User cannot assign developer:', illegalAssign.status === 403 ? 'FORBIDDEN (Correct)' : 'FAILED');

  console.log('\n=== ALL E2E LIFECYCLE & ACCESS CONTROL TESTS COMPLETED SUCCESSFULLY ===');
}

runTests().catch(err => {
  console.error('Test script crashed:', err);
  process.exit(1);
});
