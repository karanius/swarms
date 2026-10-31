---
license: apache-2.0
language:
- en
base_model:
- nari-labs/Dia-1.6B
pipeline_tag: text-to-speech
library_name: mlx
---

# mlx-community/Dia-1.6B
This model was converted to MLX format from [`nari-labs/Dia-1.6B`]() using mlx-audio version **0.0.4**.
Refer to the [original model card](https://huggingface.co/nari-labs/Dia-1.6B) for more details on the model.
## Use with mlx

```bash
pip install -U mlx-audio
```

```bash
python -m mlx_audio.tts.generate --model mlx-community/Dia-1.6B \
--text "[S1] Dia is an open weights text to dialogue model. [S2] You get full control over scripts and voices. [S1] Wow. Amazing. (laughs) [S2] Try it now on Git hub or Hugging Face."
```
