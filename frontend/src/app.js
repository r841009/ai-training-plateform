import { createApp, computed, reactive, toRefs, onMounted } from 'vue';
import ElementPlus, { ElMessage } from 'element-plus';
import { Cpu, MagicStick, Plus, Refresh, Upload, VideoPlay } from '@element-plus/icons-vue';

const API_BASE = new URLSearchParams(location.search).has('mock')
  ? 'mock'
  : localStorage.getItem('apiBase') || 'mock';
const USE_MOCK = API_BASE === 'mock';

const now = () => new Date().toISOString();
const id = (name) => `${name}-${Math.random().toString(16).slice(2, 10)}`;

const mockDb = {
  baseModels: [{
    id: 'base-fasterrcnn',
    name: 'fasterrcnn_resnet50_fpn',
    family: 'torchvision_detection',
    task_type: 'object_detection',
  }],
  trainers: [{
    id: 'trainer-mock',
    trainer_name: 'mock_train',
    base_model_family: 'torchvision_detection',
  }],
  projects: [{
    id: 'project-demo',
    project_code: 'AOI_DEMO',
    name: 'AOI Demo',
    description: 'Standalone demo project',
    created_at: now(),
    updated_at: now(),
  }],
  datasets: [{
    id: 'dataset-demo',
    project_id: 'project-demo',
    version_no: 1,
    status: 'READY',
    storage_path: 'mock/storage/dataset-demo',
    description: 'Ready demo dataset',
    created_at: now(),
    updated_at: now(),
  }],
  jobs: [],
  models: [{
    id: 'model-demo',
    project_id: 'project-demo',
    training_job_id: 'job-demo',
    dataset_version_id: 'dataset-demo',
    base_model_id: 'base-fasterrcnn',
    parent_model_version_id: null,
    version_no: 1,
    name: 'AOI_DEMO_fasterrcnn_resnet50_fpn_demo',
    artifact_path: 'mock/storage/model-demo',
    metrics_json: {},
    created_at: now(),
  }],
  evaluationDatasets: [],
  results: [],
};

const payload = (options) => options.body instanceof FormData ? {} : JSON.parse(options.body || '{}');

async function mockApi(path, options = {}) {
  const method = options.method || 'GET';
  const parts = path.split('/').filter(Boolean);
  const projectId = parts[1];
  const collection = parts[2];
  const itemId = parts[3];
  const body = payload(options);

  if (path === '/base-models') return mockDb.baseModels;
  if (path === '/trainers') return mockDb.trainers;
  if (path === '/projects' && method === 'GET') return mockDb.projects;
  if (path === '/projects' && method === 'POST') {
    const project = { id: id('project'), ...body, created_at: now(), updated_at: now() };
    mockDb.projects.unshift(project);
    return project;
  }
  if (path === '/scheduler/dispatch-once') {
    const pending = mockDb.jobs.filter((job) => ['PENDING', 'RESUMABLE'].includes(job.status));
    pending.forEach((job) => {
      job.status = 'SUCCESS';
      mockDb.models.push({
        id: id('model'),
        project_id: job.project_id,
        training_job_id: job.id,
        dataset_version_id: job.dataset_version_id,
        base_model_id: job.base_model_id,
        parent_model_version_id: job.training_config_json.parent_model_version_id || null,
        version_no: mockDb.models.filter((m) => m.project_id === job.project_id).length + 1,
        name: `${mockDb.projects.find((p) => p.id === job.project_id)?.project_code || 'PROJECT'}_mock_model`,
        artifact_path: `mock/storage/${job.id}`,
        metrics_json: {},
        created_at: now(),
      });
    });
    return { dispatched: pending.length, queued: 0, failed: 0 };
  }

  if (parts[0] !== 'projects') throw new Error(`Mock route not found: ${path}`);

  if (collection === 'datasets' && method === 'GET') return mockDb.datasets.filter((d) => d.project_id === projectId);
  if (collection === 'datasets' && method === 'POST' && parts.length === 3) {
    const dataset = {
      id: id('dataset'),
      project_id: projectId,
      version_no: mockDb.datasets.filter((d) => d.project_id === projectId).length + 1,
      status: 'PENDING',
      storage_path: `mock/storage/${projectId}`,
      description: body.description,
      created_at: now(),
      updated_at: now(),
    };
    mockDb.datasets.unshift(dataset);
    return dataset;
  }
  if (collection === 'datasets' && parts[4] === 'upload') {
    mockDb.datasets.find((d) => d.id === itemId).status = 'UPLOADED';
    return mockDb.datasets.find((d) => d.id === itemId);
  }
  if (collection === 'datasets' && parts[4] === 'process') {
    mockDb.datasets.find((d) => d.id === itemId).status = 'READY';
    return mockDb.datasets.find((d) => d.id === itemId);
  }
  if (collection === 'training-jobs' && method === 'GET') return mockDb.jobs.filter((j) => j.project_id === projectId);
  if (collection === 'training-jobs' && method === 'POST' && parts.length === 3) {
    const job = {
      id: id('job'),
      project_id: projectId,
      assigned_server_id: null,
      status: 'PENDING',
      failure_reason: null,
      created_at: now(),
      updated_at: now(),
      ...body,
    };
    mockDb.jobs.unshift(job);
    return job;
  }
  if (collection === 'training-jobs' && parts[4] === 'resume') {
    mockDb.jobs.find((j) => j.id === itemId).status = 'RESUMABLE';
    return mockDb.jobs.find((j) => j.id === itemId);
  }
  if (collection === 'model-versions' && method === 'GET') return mockDb.models.filter((m) => m.project_id === projectId);
  if (collection === 'model-versions' && parts[4] === 'retrain') {
    const parent = mockDb.models.find((m) => m.id === itemId);
    const job = {
      id: id('job'),
      project_id: projectId,
      dataset_version_id: parent.dataset_version_id,
      base_model_id: parent.base_model_id,
      trainer_id: 'trainer-mock',
      assigned_server_id: null,
      status: 'PENDING',
      resource_requirement_json: { required_gpu_memory_gb: 8 },
      training_config_json: { epochs: 1, parent_model_version_id: parent.id },
      failure_reason: null,
      created_at: now(),
      updated_at: now(),
    };
    mockDb.jobs.unshift(job);
    return job;
  }
  if (collection === 'model-versions' && parts[4] === 'evaluate') {
    const model = mockDb.models.find((m) => m.id === itemId);
    const result = {
      id: id('eval'),
      project_id: projectId,
      model_version_id: itemId,
      dataset_version_id: model.dataset_version_id,
      evaluation_dataset_id: body.evaluation_dataset_id || null,
      metrics_json: { accuracy: 0.9, precision: 0.88, recall: 0.86, f1: 0.87 },
      report_path: `mock/storage/${itemId}/evaluation_report.json`,
      sample_predictions_path: `mock/storage/${itemId}/sample_predictions.json`,
      created_at: now(),
    };
    mockDb.results.unshift(result);
    return result;
  }
  if (collection === 'evaluation-datasets' && method === 'GET') {
    return mockDb.evaluationDatasets.filter((d) => d.project_id === projectId);
  }
  if (collection === 'evaluation-datasets' && method === 'POST') {
    const dataset = { id: id('eval-dataset'), project_id: projectId, description: null, created_at: now(), ...body };
    mockDb.evaluationDatasets.unshift(dataset);
    return dataset;
  }
  if (collection === 'evaluation-results' && method === 'GET') {
    return mockDb.results.filter((r) => r.project_id === projectId);
  }

  throw new Error(`Mock route not found: ${path}`);
}

async function api(path, options = {}) {
  if (USE_MOCK) return mockApi(path, options);

  const response = await fetch(`${API_BASE}${path}`, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok || body.success === false) {
    throw new Error(body.error?.message || response.statusText || 'Request failed');
  }
  return body.data;
}

const emptyJobForm = () => ({
  dataset_version_id: '',
  base_model_id: '',
  trainer_id: '',
});

createApp({
  template: '#app-template',
  setup() {
    const state = reactive({
      activeTab: 'overview',
      apiMode: USE_MOCK ? 'mock' : 'api',
      baseModels: [],
      datasetForm: { description: '' },
      datasets: [],
      error: '',
      epochs: 1,
      evaluationDatasets: [],
      evalDatasetForm: { name: '', dataset_version_id: '', storage_path: '' },
      jobForm: emptyJobForm(),
      jobs: [],
      loading: false,
      models: [],
      projectForm: { project_code: '', name: '', description: '' },
      projects: [],
      results: [],
      selectedDatasetId: '',
      selectedEvaluationDatasetId: '',
      selectedProjectId: '',
      trainers: [],
      uploadFile: null,
    });

    const selectedProject = computed(() => state.projects.find((p) => p.id === state.selectedProjectId));
    const readyDatasets = computed(() => state.datasets.filter((d) => d.status === 'READY'));

    const run = async (task, success) => {
      state.error = '';
      state.loading = true;
      try {
        await task();
        if (success) ElMessage.success(success);
      } catch (err) {
        state.error = err.message;
      } finally {
        state.loading = false;
      }
    };

    const loadCatalog = async () => {
      [state.baseModels, state.trainers] = await Promise.all([api('/base-models'), api('/trainers')]);
    };

    const loadProjects = async () => {
      state.projects = await api('/projects');
      if (!state.selectedProjectId && state.projects.length) state.selectedProjectId = state.projects[0].id;
    };

    const refreshProject = async () => {
      if (!state.selectedProjectId) return;
      const id = state.selectedProjectId;
      [
        state.datasets,
        state.jobs,
        state.models,
        state.evaluationDatasets,
        state.results,
      ] = await Promise.all([
        api(`/projects/${id}/datasets`),
        api(`/projects/${id}/training-jobs`),
        api(`/projects/${id}/model-versions`),
        api(`/projects/${id}/evaluation-datasets`),
        api(`/projects/${id}/evaluation-results`),
      ]);
    };

    const loadAll = () => run(async () => {
      await Promise.all([loadCatalog(), loadProjects()]);
      await refreshProject();
    });

    const selectProject = (id) => run(async () => {
      state.selectedProjectId = id;
      await refreshProject();
    });

    const createProject = () => run(async () => {
      const project = await api('/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(state.projectForm),
      });
      state.projectForm = { project_code: '', name: '', description: '' };
      state.selectedProjectId = project.id;
      await loadProjects();
      await refreshProject();
    }, 'Project created');

    const createDataset = () => run(async () => {
      const dataset = await api(`/projects/${state.selectedProjectId}/datasets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: state.datasetForm?.description || null }),
      });
      state.datasetForm = { description: '' };
      state.selectedDatasetId = dataset.id;
      await refreshProject();
    }, 'Dataset created');

    const setUploadFile = (event) => {
      state.uploadFile = event.target.files?.[0] || null;
    };

    const uploadDataset = () => run(async () => {
      const form = new FormData();
      form.append('file', state.uploadFile);
      await api(`/projects/${state.selectedProjectId}/datasets/${state.selectedDatasetId}/upload`, {
        method: 'POST',
        body: form,
      });
      state.uploadFile = null;
      await refreshProject();
    }, 'Dataset uploaded');

    const processDataset = () => run(async () => {
      await api(`/projects/${state.selectedProjectId}/datasets/${state.selectedDatasetId}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      await refreshProject();
    }, 'Dataset processed');

    const pickTrainer = () => {
      const model = state.baseModels.find((m) => m.id === state.jobForm.base_model_id);
      const trainer = state.trainers.find((t) => t.base_model_family === model?.family);
      state.jobForm.trainer_id = trainer?.id || '';
    };

    const createTrainingJob = () => run(async () => {
      await api(`/projects/${state.selectedProjectId}/training-jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...state.jobForm,
          resource_requirement_json: { required_gpu_memory_gb: 8 },
          training_config_json: { epochs: state.epochs },
        }),
      });
      state.jobForm = emptyJobForm();
      await refreshProject();
    }, 'Training job created');

    const resumeJob = (jobId) => run(async () => {
      await api(`/projects/${state.selectedProjectId}/training-jobs/${jobId}/resume`, { method: 'POST' });
      await refreshProject();
    }, 'Job resumed');

    const dispatchOnce = () => run(async () => {
      await api('/scheduler/dispatch-once', { method: 'POST' });
      await refreshProject();
    }, 'Dispatch finished');

    const createEvaluationDataset = () => run(async () => {
      await api(`/projects/${state.selectedProjectId}/evaluation-datasets`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: state.evalDatasetForm.name,
          dataset_version_id: state.evalDatasetForm.dataset_version_id || null,
          storage_path: state.evalDatasetForm.storage_path || null,
        }),
      });
      state.evalDatasetForm = { name: '', dataset_version_id: '', storage_path: '' };
      await refreshProject();
    }, 'Evaluation dataset created');

    const evaluate = (modelId) => run(async () => {
      await api(`/projects/${state.selectedProjectId}/model-versions/${modelId}/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ evaluation_dataset_id: state.selectedEvaluationDatasetId || null }),
      });
      await refreshProject();
      state.activeTab = 'evaluations';
    }, 'Evaluation finished');

    const retrain = (modelId) => run(async () => {
      await api(`/projects/${state.selectedProjectId}/model-versions/${modelId}/retrain`, { method: 'POST' });
      await refreshProject();
      state.activeTab = 'jobs';
    }, 'Retrain job created');

    const datasetLabel = (dataset) => `v${dataset.version_no} ${dataset.status}`;
    const jsonLine = (value) => JSON.stringify(value || {});
    const shortId = (id) => id ? id.slice(0, 8) : '';

    onMounted(loadAll);

    return {
      ...toRefs(state),
      Cpu,
      MagicStick,
      Plus,
      Refresh,
      Upload,
      VideoPlay,
      createDataset,
      createEvaluationDataset,
      createProject,
      createTrainingJob,
      datasetLabel,
      dispatchOnce,
      evaluate,
      jsonLine,
      loadAll,
      pickTrainer,
      processDataset,
      readyDatasets,
      refreshProject: () => run(refreshProject),
      resumeJob,
      retrain,
      selectProject,
      selectedProject,
      setUploadFile,
      shortId,
      uploadDataset,
    };
  },
}).use(ElementPlus).mount('#app');
