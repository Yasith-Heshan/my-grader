import React, { useState, useEffect } from 'react';
import {
    Box,
    Button,
    Card,
    CardContent,
    CardActions,
    Typography,
    Grid,
    Chip,
    IconButton,
    Alert,
    CircularProgress,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
    Tooltip,
    GridProps,
} from '@mui/material';
import {
    Add as AddIcon,
    Delete as DeleteIcon,
    Refresh as RefreshIcon,
    CheckCircle as SuccessIcon,
    Error as ErrorIcon,
    HourglassEmpty as PendingIcon,
    CloudUpload as UploadIcon,
} from '@mui/icons-material';
import axios from '../api/axiosInstance';
import CustomDockerImageDialog from './CustomDockerImageDialog';

interface CustomDockerImage {
    id: string;
    name: string;
    description: string;
    docker_hub_username: string;
    full_image_name: string;
    base_image: string;
    packages: string[];
    status: string;
    build_error?: string;
    size_mb?: number;
    build_time_seconds?: number;
    created_at: string;
    updated_at: string;
    uploaded_at?: string;
    usage_count: number;
}

const STATUS_CONFIG = {
    pending: { color: 'default' as const, icon: <PendingIcon />, label: 'Pending' },
    building: { color: 'info' as const, icon: <CircularProgress size={16} />, label: 'Building' },
    success: { color: 'success' as const, icon: <SuccessIcon />, label: 'Built' },
    uploading: { color: 'info' as const, icon: <UploadIcon />, label: 'Uploading' },
    uploaded: { color: 'success' as const, icon: <SuccessIcon />, label: 'Ready' },
    failed: { color: 'error' as const, icon: <ErrorIcon />, label: 'Failed' },
};

export const CustomDockerImageManager: React.FC = () => {
    const [images, setImages] = useState<CustomDockerImage[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [imageToDelete, setImageToDelete] = useState<CustomDockerImage | null>(null);

    const fetchImages = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await axios.get('/api/teacher/custom-images');
            // Ensure response.data is an array
            setImages(Array.isArray(response.data) ? response.data : []);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load custom images');
            setImages([]); // Reset to empty array on error
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchImages();
    }, []);

    const handleDeleteClick = (image: CustomDockerImage) => {
        setImageToDelete(image);
        setDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!imageToDelete) return;

        try {
            await axios.delete(`/api/teacher/custom-images/${imageToDelete.id}`);
            setImages(images.filter(img => img.id !== imageToDelete.id));
            setDeleteDialogOpen(false);
            setImageToDelete(null);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to delete image');
        }
    };

    const handleImageCreated = () => {
        fetchImages();
    };

    const formatSize = (sizeMb?: number) => {
        if (!sizeMb) return 'N/A';
        return `${sizeMb.toFixed(1)} MB`;
    };

    const formatBuildTime = (seconds?: number) => {
        if (!seconds) return 'N/A';
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return minutes > 0 ? `${minutes}m ${remainingSeconds}s` : `${remainingSeconds}s`;
    };

    if (loading && images.length === 0) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    return (
        <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h5">Custom Docker Images</Typography>
                <Box>
                    <IconButton onClick={fetchImages} sx={{ mr: 1 }}>
                        <RefreshIcon />
                    </IconButton>
                    <Button
                        variant="contained"
                        startIcon={<AddIcon />}
                        onClick={() => setDialogOpen(true)}
                    >
                        Create Custom Image
                    </Button>
                </Box>
            </Box>

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            {images.length === 0 ? (
                <Card>
                    <CardContent>
                        <Typography variant="body1" color="text.secondary" align="center">
                            No custom Docker images yet. Create one to get started!
                        </Typography>
                    </CardContent>
                </Card>
            ) : (
                <Grid container spacing={3}>
                    {images.map((image) => {
                        const statusConfig = STATUS_CONFIG[image.status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.pending;

                        return (
                            <Grid {...({ item: true, xs: 12, md: 6, lg: 4 } as GridProps)} key={image.id}>
                                <Card>
                                    <CardContent>
                                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                                            <Typography variant="h6" component="div">
                                                {image.name}
                                            </Typography>
                                            <Chip
                                                label={statusConfig.label}
                                                color={statusConfig.color}
                                                size="small"
                                                icon={statusConfig.icon}
                                            />
                                        </Box>

                                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                                            {image.description}
                                        </Typography>

                                        <Box sx={{ mb: 2 }}>
                                            <Typography variant="caption" color="text.secondary" display="block">
                                                Image Name:
                                            </Typography>
                                            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                                                {image.full_image_name}
                                            </Typography>
                                        </Box>

                                        <Box sx={{ mb: 2 }}>
                                            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
                                                Packages ({image.packages.length}):
                                            </Typography>
                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                                {image.packages.slice(0, 3).map((pkg, idx) => (
                                                    <Chip key={idx} label={pkg} size="small" variant="outlined" />
                                                ))}
                                                {image.packages.length > 3 && (
                                                    <Chip label={`+${image.packages.length - 3} more`} size="small" variant="outlined" />
                                                )}
                                            </Box>
                                        </Box>

                                        <Grid container spacing={1} sx={{ mb: 1 }}>
                                            <Grid {...({ item: true, xs: 6 } as GridProps)}>
                                                <Typography variant="caption" color="text.secondary">
                                                    Size:
                                                </Typography>
                                                <Typography variant="body2">
                                                    {formatSize(image.size_mb)}
                                                </Typography>
                                            </Grid>
                                            <Grid {...({ item: true, xs: 6 } as GridProps)}>
                                                <Typography variant="caption" color="text.secondary">
                                                    Build Time:
                                                </Typography>
                                                <Typography variant="body2">
                                                    {formatBuildTime(image.build_time_seconds)}
                                                </Typography>
                                            </Grid>
                                            <Grid {...({ item: true, xs: 6 } as GridProps)}>
                                                <Typography variant="caption" color="text.secondary">
                                                    Used By:
                                                </Typography>
                                                <Typography variant="body2">
                                                    {image.usage_count} assignment(s)
                                                </Typography>
                                            </Grid>
                                            <Grid {...({ item: true, xs: 6 } as GridProps)}>
                                                <Typography variant="caption" color="text.secondary">
                                                    Created:
                                                </Typography>
                                                <Typography variant="body2" sx={{ fontSize: '0.75rem' }}>
                                                    {new Date(image.created_at).toLocaleDateString()}
                                                </Typography>
                                            </Grid>
                                        </Grid>

                                        {image.build_error && (
                                            <Alert severity="error" sx={{ mt: 2 }}>
                                                <Typography variant="caption">
                                                    {image.build_error}
                                                </Typography>
                                            </Alert>
                                        )}
                                    </CardContent>

                                    <CardActions>
                                        <Tooltip title={image.usage_count > 0 ? 'Cannot delete image in use' : 'Delete image'}>
                                            <span>
                                                <IconButton
                                                    size="small"
                                                    color="error"
                                                    onClick={() => handleDeleteClick(image)}
                                                    disabled={image.usage_count > 0}
                                                >
                                                    <DeleteIcon />
                                                </IconButton>
                                            </span>
                                        </Tooltip>
                                    </CardActions>
                                </Card>
                            </Grid>
                        );
                    })}
                </Grid>
            )}

            <CustomDockerImageDialog
                open={dialogOpen}
                onClose={() => setDialogOpen(false)}
                onImageCreated={handleImageCreated}
            />

            <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
                <DialogTitle>Delete Custom Image</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Are you sure you want to delete the image "{imageToDelete?.name}"?
                        This action cannot be undone.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
                    <Button onClick={handleDeleteConfirm} color="error" variant="contained">
                        Delete
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
};

export default CustomDockerImageManager;
