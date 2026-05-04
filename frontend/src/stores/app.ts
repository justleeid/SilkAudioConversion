import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { FileInfo, TaskInfo, TaskStatus } from '@/types';
import * as convertApi from '@/api/convert';

export const useAppStore = defineStore('app', () => {
  // 已上传的文件列表
  const files = ref<FileInfo[]>([]);

  // 转换任务列表
  const tasks = ref<Map<string, TaskInfo>>(new Map());

  // PLIST 合并中选中的文件 ID
  const selectedForPlist = ref<Set<string>>(new Set());

  /**
   * 上传文件
   */
  async function uploadFiles(fileList: FileList) {
    const filesToUpload: File[] = [];
    for (let i = 0; i < fileList.length; i++) {
      filesToUpload.push(fileList[i]);
    }

    const response = await convertApi.upload(filesToUpload);
    if (response.code === 0 && response.data?.files) {
      files.value = response.data.files;

      // 为每个上传的文件创建任务
      response.data.files.forEach(file => {
        tasks.value.set(file.task_id, {
          task_id: file.task_id,
          status: TaskStatus.PENDING,
          progress: 0,
        });
      });
    }

    return response;
  }

  /**
   * 开始转换
   */
  async function convert(taskId: string, targetFormat: string) {
    const response = await convertApi.convert(taskId, {
      target_format: targetFormat,
      wechat_compatible: true,
    });

    if (response.code === 0) {
      const task = tasks.value.get(taskId);
      if (task) {
        task.status = TaskStatus.PROCESSING;
        task.progress = 0;

        // 定期查询状态
        queryStatusPeriodically(taskId);
      }
    }

    return response;
  }

  /**
   * 定期查询任务状态
   */
  function queryStatusPeriodically(taskId: string, interval = 1000, maxRetries = 100) {
    let retries = 0;

    const timer = setInterval(async () => {
      const response = await convertApi.queryStatus(taskId);

      if (response.code === 0 && response.data) {
        const taskInfo = response.data;
        tasks.value.set(taskId, taskInfo);

        // 如果任务完成或失败，停止轮询
        if (
          taskInfo.status === TaskStatus.COMPLETED ||
          taskInfo.status === TaskStatus.FAILED
        ) {
          clearInterval(timer);
        }
      }

      retries++;
      if (retries >= maxRetries) {
        clearInterval(timer);
      }
    }, interval);
  }

  /**
   * 下载文件
   */
  function downloadFile(taskId: string) {
    convertApi.download(taskId);
  }

  /**
   * 选择所有 PLIST 文件
   */
  function selectAllForPlist() {
    files.value.forEach(file => {
      selectedForPlist.value.add(file.task_id);
    });
  }

  /**
   * 清除 PLIST 选择
   */
  function clearPlistSelection() {
    selectedForPlist.value.clear();
  }

  /**
   * 切换文件选择
   */
  function togglePlistSelection(taskId: string) {
    if (selectedForPlist.value.has(taskId)) {
      selectedForPlist.value.delete(taskId);
    } else {
      selectedForPlist.value.add(taskId);
    }
  }

  return {
    files,
    tasks,
    selectedForPlist,
    uploadFiles,
    convert,
    downloadFile,
    selectAllForPlist,
    clearPlistSelection,
    togglePlistSelection,
  };
});
