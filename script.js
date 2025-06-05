const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let bird = { x: 50, y: 150, width: 30, height: 30, velocity: 0 };
let gravity = 0.5;
let lift = -8;
let pipes = [];
let score = 0;
let gameOver = false;

document.addEventListener('keydown', (e) => {
  if (e.code === 'Space' || e.code === 'ArrowUp') {
    bird.velocity = lift;
  }
});

function drawBird() {
  ctx.fillStyle = 'yellow';
  ctx.fillRect(bird.x, bird.y, bird.width, bird.height);
}

function drawPipes() {
  ctx.fillStyle = 'green';
  pipes.forEach(pipe => {
    ctx.fillRect(pipe.x, 0, pipe.width, pipe.top);
    ctx.fillRect(pipe.x, pipe.top + pipe.gap, pipe.width, canvas.height - pipe.top - pipe.gap);
  });
}

function updatePipes() {
  for (let pipe of pipes) {
    pipe.x -= 2;

    if (!pipe.passed && pipe.x < bird.x) {
      pipe.passed = true;
      score++;
    }

    if (
      bird.x < pipe.x + pipe.width &&
      bird.x + bird.width > pipe.x &&
      (bird.y < pipe.top || bird.y + bird.height > pipe.top + pipe.gap)
    ) {
      gameOver = true;
    }
  }

  if (pipes.length === 0 || pipes[pipes.length - 1].x < 200) {
    let top = Math.random() * 300 + 50;
    pipes.push({ x: canvas.width, top, width: 50, gap: 130, passed: false });
  }

  if (pipes[0].x + pipes[0].width < 0) {
    pipes.shift();
  }
}

function showScore() {
  ctx.fillStyle = "black";
  ctx.font = "24px Arial";
  ctx.fillText(`Score: ${score}`, 10, 30);
}

function resetGame() {
  bird.y = 150;
  bird.velocity = 0;
  pipes = [];
  score = 0;
  gameOver = false;
}

function gameLoop() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (!gameOver) {
    bird.velocity += gravity;
    bird.y += bird.velocity;

    if (bird.y + bird.height > canvas.height || bird.y < 0) {
      gameOver = true;
    }

    updatePipes();
    drawPipes();
    drawBird();
    showScore();

  } else {
    ctx.fillStyle = "red";
    ctx.font = "36px Arial";
    ctx.fillText("Game Over", 100, 250);
    ctx.font = "20px Arial";
    ctx.fillText("Press R to restart", 120, 290);
  }

  requestAnimationFrame(gameLoop);
}

document.addEventListener('keydown', (e) => {
  if (e.code === 'KeyR' && gameOver) {
    resetGame();
  }
});

resetGame();
gameLoop();
