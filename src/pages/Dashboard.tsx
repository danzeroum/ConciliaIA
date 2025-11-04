import { Box, Typography, Container, Paper, Grid } from '@mui/material';

export default function Dashboard() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Total de Vendas</Typography>
            <Typography variant="h4">R$ 0,00</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Transações</Typography>
            <Typography variant="h4">0</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6">Divergências</Typography>
            <Typography variant="h4">0</Typography>
          </Paper>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3 }}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Bem-vindo ao ConciliaAI MVP
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sistema de reconciliação financeira com IA
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}
