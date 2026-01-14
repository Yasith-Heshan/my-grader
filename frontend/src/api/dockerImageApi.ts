import axiosInstance from './axiosInstance';

export interface CustomDockerImage {
    id: string;
    _id?: string;
    name: string;
    description?: string;
    base_image: string;
    packages?: string[];
    pip_install_commands?: string;
    docker_hub_tag?: string;
    status: 'pending' | 'building' | 'uploading' | 'uploaded' | 'failed';
    teacher_id: string;
    created_at: string;
    updated_at: string;
    build_logs?: string;
    error_message?: string;
}

export const dockerImageApi = {
    // Get all uploaded Docker images for the current teacher
    getUploaded: async (): Promise<CustomDockerImage[]> => {
        const response = await axiosInstance.get('/api/teacher/custom-images', {
            params: { status_filter: 'uploaded' }
        });
        return response.data.map((img: any) => ({
            ...img,
            id: img.id || img._id
        }));
    },

    // Get all Docker images for the current teacher
    getAll: async (): Promise<CustomDockerImage[]> => {
        const response = await axiosInstance.get('/api/teacher/custom-images');
        return response.data.map((img: any) => ({
            ...img,
            id: img.id || img._id
        }));
    },

    // Get a specific Docker image by ID
    getById: async (imageId: string): Promise<CustomDockerImage> => {
        const response = await axiosInstance.get(`/api/teacher/custom-images/${imageId}`);
        return {
            ...response.data,
            id: response.data.id || response.data._id
        };
    }
};
