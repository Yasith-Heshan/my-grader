import React, { useState } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Chip,
    Box,
    Typography,
    Alert,
    LinearProgress,
    IconButton,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Stepper,
    Step,
    StepLabel,
    Switch,
    FormControlLabel,
} from '@mui/material';
import {
    Add as AddIcon,
    Delete as DeleteIcon,
    CloudUpload as UploadIcon,
} from '@mui/icons-material';
import axios from '../api/axiosInstance';

interface CustomDockerImageDialogProps {
    open: boolean;
    onClose: () => void;
    onImageCreated: () => void;
}

interface PackageInput {
    name: string;
    version: string;
}

const BASE_IMAGES = [
    { value: 'python:3.11-alpine', label: 'Python 3.11 Alpine (Lightweight)' },
    { value: 'python:3.11-slim', label: 'Python 3.11 Slim (Standard)' },
    { value: 'python:3.11', label: 'Python 3.11 Full' },
];

const COMMON_PACKAGES = [
    'numpy',
    'pandas',
    'matplotlib',
    'scipy',
    'seaborn',
    'scikit-learn',
    'requests',
    'beautifulsoup4',
    'sqlalchemy',
    'pytest',
];

export const CustomDockerImageDialog: React.FC<CustomDockerImageDialogProps> = ({
    open,
    onClose,
    onImageCreated,
}) => {
    const [activeStep, setActiveStep] = useState(0);
    const [imageName, setImageName] = useState('');
    const [description, setDescription] = useState('');
    const [baseImage, setBaseImage] = useState('python:3.11-alpine');
    const [packages, setPackages] = useState<PackageInput[]>([{ name: '', version: '' }]);
    const [pipCommands, setPipCommands] = useState<string>('');
    const [useRawPipCommands, setUseRawPipCommands] = useState(false);
    const [dockerHubUsername, setDockerHubUsername] = useState('');
    const [dockerHubPassword, setDockerHubPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const steps = ['Basic Info', 'Packages', 'Docker Hub'];

    const handleAddPackage = () => {
        setPackages([...packages, { name: '', version: '' }]);
    };

    const handleRemovePackage = (index: number) => {
        setPackages(packages.filter((_, i) => i !== index));
    };

    const handlePackageChange = (index: number, field: 'name' | 'version', value: string) => {
        const newPackages = [...packages];
        newPackages[index][field] = value;
        setPackages(newPackages);
    };

    const handleQuickAddPackage = (packageName: string) => {
        // Check if package already exists
        const exists = packages.some(p => p.name === packageName);
        if (exists) return;

        // Add to first empty slot or create new one
        const emptyIndex = packages.findIndex(p => !p.name);
        if (emptyIndex >= 0) {
            const newPackages = [...packages];
            newPackages[emptyIndex].name = packageName;
            setPackages(newPackages);
        } else {
            setPackages([...packages, { name: packageName, version: '' }]);
        }
    };

    const handleNext = () => {
        setError(null);

        if (activeStep === 0) {
            // Validate basic info
            if (!imageName.trim()) {
                setError('Image name is required');
                return;
            }
            if (!/^[a-z0-9][a-z0-9-]*[a-z0-9]$/.test(imageName)) {
                setError('Image name must contain only lowercase letters, numbers, and hyphens');
                return;
            }
            if (!description.trim() || description.length < 10) {
                setError('Description must be at least 10 characters');
                return;
            }
        } else if (activeStep === 1) {
            // Validate packages or pip commands
            if (useRawPipCommands) {
                if (!pipCommands.trim()) {
                    setError('Pip install commands are required');
                    return;
                }
            } else {
                const validPackages = packages.filter(p => p.name.trim());
                if (validPackages.length === 0) {
                    setError('At least one package is required');
                    return;
                }
            }
        }

        setActiveStep(prev => prev + 1);
    };

    const handleBack = () => {
        setError(null);
        setActiveStep(prev => prev - 1);
    };

    const handleSubmit = async () => {
        setError(null);

        // Validate Docker Hub credentials
        if (!dockerHubUsername.trim()) {
            setError('Docker Hub username is required');
            return;
        }
        if (!dockerHubPassword.trim()) {
            setError('Docker Hub password is required');
            return;
        }

        // Format packages or use pip commands
        let imageData: any = {
            name: imageName,
            description,
            base_image: baseImage,
            docker_hub_username: dockerHubUsername,
            docker_hub_password: dockerHubPassword,
        };

        if (useRawPipCommands) {
            imageData.pip_install_commands = pipCommands;
        } else {
            const formattedPackages = packages
                .filter(p => p.name.trim())
                .map(p => p.version ? `${p.name}==${p.version}` : p.name);
            imageData.packages = formattedPackages;
        }

        setLoading(true);

        try {
            await axios.post('/api/teacher/custom-images', imageData);

            // Reset form
            setImageName('');
            setDescription('');
            setBaseImage('python:3.11-alpine');
            setPackages([{ name: '', version: '' }]);
            setPipCommands('');
            setUseRawPipCommands(false);
            setDockerHubUsername('');
            setDockerHubPassword('');
            setActiveStep(0);

            onImageCreated();
            onClose();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to create custom image');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        setError(null);
        setActiveStep(0);
        onClose();
    };

    return (
        <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
            <DialogTitle>
                Create Custom Docker Image
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Build a custom Python environment with your required packages
                </Typography>
            </DialogTitle>

            <DialogContent>
                <Stepper activeStep={activeStep} sx={{ mb: 3, mt: 2 }}>
                    {steps.map((label) => (
                        <Step key={label}>
                            <StepLabel>{label}</StepLabel>
                        </Step>
                    ))}
                </Stepper>

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                        {error}
                    </Alert>
                )}

                {/* Step 0: Basic Info */}
                {activeStep === 0 && (
                    <Box>
                        <TextField
                            label="Image Name"
                            fullWidth
                            value={imageName}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setImageName(e.target.value.toLowerCase())}
                            placeholder="ml-environment"
                            helperText="Use lowercase letters, numbers, and hyphens only"
                            sx={{ mb: 2 }}
                        />

                        <TextField
                            label="Description"
                            fullWidth
                            multiline
                            rows={3}
                            value={description}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDescription(e.target.value)}
                            placeholder="Machine learning environment with scikit-learn and tensorflow"
                            helperText="Describe what this image is used for"
                            sx={{ mb: 2 }}
                        />

                        <FormControl fullWidth>
                            <InputLabel>Base Image</InputLabel>
                            <Select
                                value={baseImage}
                                onChange={(e: any) => setBaseImage(e.target.value)}
                                label="Base Image"
                            >
                                {BASE_IMAGES.map((img) => (
                                    <MenuItem key={img.value} value={img.value}>
                                        {img.label}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </Box>
                )}

                {/* Step 1: Packages */}
                {activeStep === 1 && (
                    <Box>
                        <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
                            <Typography variant="subtitle1">Package Configuration:</Typography>
                            <FormControlLabel
                                control={
                                    <Switch
                                        checked={useRawPipCommands}
                                        onChange={(e) => setUseRawPipCommands(e.target.checked)}
                                    />
                                }
                                label="Use Raw Pip Commands"
                            />
                        </Box>

                        {!useRawPipCommands ? (
                            <>
                                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                                    Quick Add Common Packages:
                                </Typography>
                                <Box sx={{ mb: 3, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                    {COMMON_PACKAGES.map((pkg) => {
                                        const isAdded = packages.some(p => p.name === pkg);
                                        return (
                                            <Chip
                                                key={pkg}
                                                label={pkg}
                                                onClick={() => handleQuickAddPackage(pkg)}
                                                color={isAdded ? 'primary' : 'default'}
                                                variant={isAdded ? 'filled' : 'outlined'}
                                            />
                                        );
                                    })}
                                </Box>

                                <Typography variant="subtitle2" sx={{ mb: 2 }}>
                                    Packages to Install:
                                </Typography>

                                {packages.map((pkg, index) => (
                                    <Box key={index} sx={{ display: 'flex', gap: 1, mb: 2 }}>
                                        <TextField
                                            label="Package Name"
                                            value={pkg.name}
                                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => handlePackageChange(index, 'name', e.target.value)}
                                            placeholder="numpy"
                                            sx={{ flex: 2 }}
                                        />
                                        <TextField
                                            label="Version (optional)"
                                            value={pkg.version}
                                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => handlePackageChange(index, 'version', e.target.value)}
                                            placeholder="1.24.3"
                                            sx={{ flex: 1 }}
                                        />
                                        <IconButton
                                            onClick={() => handleRemovePackage(index)}
                                            disabled={packages.length === 1}
                                            color="error"
                                        >
                                            <DeleteIcon />
                                        </IconButton>
                                    </Box>
                                ))}

                                <Button
                                    startIcon={<AddIcon />}
                                    onClick={handleAddPackage}
                                    variant="outlined"
                                    size="small"
                                >
                                    Add Package
                                </Button>
                            </>
                        ) : (
                            <>
                                <Alert severity="info" sx={{ mb: 2 }}>
                                    Enter pip install commands directly. Each line will be executed as a separate RUN command in the Dockerfile.
                                    Examples: "numpy==1.24.3", "pandas matplotlib", "scikit-learn&gt;=1.0.0", etc.
                                </Alert>

                                <TextField
                                    label="Pip Install Commands"
                                    fullWidth
                                    multiline
                                    rows={8}
                                    value={pipCommands}
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPipCommands(e.target.value)}
                                    placeholder="numpy==1.24.3&#10;pandas&gt;=2.0.0&#10;matplotlib&#10;scikit-learn&gt;=1.0.0 scipy"
                                    helperText="One or more packages per line. You can specify versions using ==, &gt;=, &lt;=, etc."
                                    sx={{ fontFamily: 'monospace' }}
                                />
                            </>
                        )}
                    </Box>
                )}

                {/* Step 2: Docker Hub */}
                {activeStep === 2 && (
                    <Box>
                        <Alert severity="info" sx={{ mb: 2 }}>
                            Your Docker Hub credentials are used to upload the built image.
                            They are not stored and are only used for this operation.
                        </Alert>

                        <TextField
                            label="Docker Hub Username"
                            fullWidth
                            value={dockerHubUsername}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDockerHubUsername(e.target.value)}
                            placeholder="yourusername"
                            sx={{ mb: 2 }}
                        />

                        <TextField
                            label="Docker Hub Password"
                            fullWidth
                            type="password"
                            value={dockerHubPassword}
                            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDockerHubPassword(e.target.value)}
                            placeholder="••••••••"
                            helperText="Your password is encrypted and not stored"
                            sx={{ mb: 2 }}
                        />

                        <Alert severity="success" sx={{ mt: 2 }}>
                            <Typography variant="subtitle2" gutterBottom>
                                Image will be created as:
                            </Typography>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                                {dockerHubUsername || 'username'}/grader-{imageName || 'image-name'}:latest
                            </Typography>
                        </Alert>
                    </Box>
                )}

                {loading && (
                    <Box sx={{ mt: 2 }}>
                        <LinearProgress />
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            Building and uploading image... This may take several minutes.
                        </Typography>
                    </Box>
                )}
            </DialogContent>

            <DialogActions>
                <Button onClick={handleClose} disabled={loading}>
                    Cancel
                </Button>
                {activeStep > 0 && (
                    <Button onClick={handleBack} disabled={loading}>
                        Back
                    </Button>
                )}
                {activeStep < steps.length - 1 ? (
                    <Button onClick={handleNext} variant="contained">
                        Next
                    </Button>
                ) : (
                    <Button
                        onClick={handleSubmit}
                        variant="contained"
                        disabled={loading}
                        startIcon={<UploadIcon />}
                    >
                        Create & Upload
                    </Button>
                )}
            </DialogActions>
        </Dialog>
    );
};

export default CustomDockerImageDialog;
