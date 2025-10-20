import { Box, Typography, Paper, Button, Grid, TextField } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

export function ReconciliationPage() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Reconciliação
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Período de Reconciliação
        </Typography>

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={12} md={5}>
            <TextField
              fullWidth
              label="Data Inicial"
              type="date"
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} md={5}>
            <TextField
              fullWidth
              label="Data Final"
              type="date"
              InputLabelProps={{ shrink: true }}
            />
          </Grid>

          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<PlayArrowIcon />}
              sx={{ height: '56px' }}
            >
              Reconciliar
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Box
          sx={{
            height: 400,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'text.secondary',
          }}
        >
          <Typography>Resultados da reconciliação aparecerão aqui</Typography>
        </Box>
      </Paper>
    </Box>
  );
}
