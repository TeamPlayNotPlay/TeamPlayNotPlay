export default class Wave {
    constructor(canvas, ctx, ext) {
        this.canvas = canvas;
        this.ctx = ctx;
        this.points = [];
        this.pointCount = 10;
        this.minRadius = 50;
        this.maxRadius = 100;
        this.minDeltaRadius = 5;
        this.maxDeltaRadius = 10;
        this.centerX = this.canvas.width / 2;
        this.centerY = this.canvas.height / 2;
        Object.assign(this, ext);
    }

    init(color = "lightblue") {
        this.color = color;
        let degree = 0;
        let deltaDegree = 360 / this.pointCount;
        for (let i = 0; i < this.pointCount; i++) {
            let radius = this.randomInt(this.minRadius, this.maxRadius);
            let x = this.centerX + radius * Math.cos(degree * Math.PI / 180);
            let y = this.centerY + radius * Math.sin(degree * Math.PI / 180);
            let deltaRadius = this.randomInt(this.minDeltaRadius, this.maxDeltaRadius);
            this.points.push({
                x: x,
                y: y,
                radius: radius,
                deltaRadius: deltaRadius,
                degree: degree
            });
            degree += deltaDegree;
        }
        requestAnimationFrame(this.animate.bind(this));
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        let prev = this.points[this.points.length - 1];
        this.ctx.beginPath();
        this.ctx.fillStyle = this.color;
        this.ctx.moveTo(prev.x, prev.y);
        this.points.forEach(point => {
            // this.ctx.arc(point.x, point.y, 5, 0, Math.PI * 2, false);
            this.ctx.quadraticCurveTo(prev.x, prev.y, (prev.x+point.x)/2, (prev.y+point.y)/2);
            prev = { ...point };
            point.radius += point.deltaRadius;
            point.x = this.centerX + point.radius * Math.cos(point.degree * Math.PI / 180);
            point.y = this.centerY + point.radius * Math.sin(point.degree * Math.PI / 180);
        });
        this.ctx.fill();
        this.ctx.closePath();
        requestAnimationFrame(this.animate.bind(this));
    }

    randomInt(m, M) {
        return Math.floor(Math.random() * (M - m + 1)) + m;
    }
}
